"""
AI Assistant service — GPT-4 powered grocery price advisor.
Injects real price data as context into each conversation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging
import json

from app.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are SmartCart AI, an expert grocery price advisor for Australian shoppers.
You have access to real-time price data from Woolworths, Coles, and Aldi supermarkets.

When answering questions:
- Be specific with prices and stores
- Highlight savings opportunities
- Recommend when to buy vs wait based on price trends
- Be concise and actionable
- Format numbers as Australian dollars (e.g., $3.49)

Current price context will be provided with each message.
"""


class AIAssistant:
    """GPT-4 powered assistant with SmartCart price context."""

    def __init__(self, db: Session):
        self.db = db
        self._client = None

    def _get_client(self):
        if self._client is None and settings.openai_api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.warning("OpenAI not available")
        return self._client

    def _get_price_context(self) -> str:
        """Fetch a snapshot of current prices to inject into the prompt."""
        try:
            # Top movers
            movers_query = text("""
                WITH pn AS (
                    SELECT DISTINCT ON (product_id, store_id)
                        product_id, store_id, price AS curr
                    FROM price_history ORDER BY product_id, store_id, date_captured DESC
                ),
                pa AS (
                    SELECT DISTINCT ON (product_id, store_id)
                        product_id, store_id, price AS prev
                    FROM price_history
                    WHERE date_captured <= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY product_id, store_id, date_captured DESC
                )
                SELECT p.name, s.name AS store, pn.curr, pa.prev,
                    ROUND(((pn.curr - pa.prev) / NULLIF(pa.prev,0)*100)::NUMERIC,1) AS chg
                FROM pn JOIN pa ON pa.product_id = pn.product_id AND pa.store_id = pn.store_id
                JOIN products p ON p.id = pn.product_id
                JOIN stores s ON s.id = pn.store_id
                ORDER BY ABS(pn.curr - pa.prev) DESC LIMIT 5
            """)
            movers = self.db.execute(movers_query).mappings().all()

            # Category inflation
            cat_query = text("""
                WITH w1 AS (
                    SELECT p.category_id, AVG(ph.price) AS avg1
                    FROM price_history ph JOIN products p ON p.id=ph.product_id
                    WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY p.category_id
                ),
                w2 AS (
                    SELECT p.category_id, AVG(ph.price) AS avg2
                    FROM price_history ph JOIN products p ON p.id=ph.product_id
                    WHERE ph.date_captured BETWEEN CURRENT_DATE-INTERVAL '14 days' AND CURRENT_DATE-INTERVAL '7 days'
                    GROUP BY p.category_id
                )
                SELECT c.name, ROUND(((w1.avg1-w2.avg2)/NULLIF(w2.avg2,0)*100)::NUMERIC,1) AS wow_pct
                FROM w1 JOIN w2 ON w2.category_id=w1.category_id
                JOIN categories c ON c.id=w1.category_id
                ORDER BY wow_pct DESC LIMIT 5
            """)
            cats = self.db.execute(cat_query).mappings().all()

            # On-sale count
            sale_query = text("""
                SELECT COUNT(*) AS on_sale_count
                FROM (
                    SELECT DISTINCT ON (product_id, store_id) is_on_sale
                    FROM price_history ORDER BY product_id, store_id, date_captured DESC
                ) t WHERE is_on_sale = TRUE
            """)
            sale_count = self.db.execute(sale_query).scalar()

            ctx_lines = [
                f"Current date: today",
                f"Products currently on sale: {sale_count}",
                "",
                "Biggest price movers this week:",
            ]
            for m in movers:
                direction = "up" if float(m["chg"] or 0) > 0 else "down"
                ctx_lines.append(
                    f"  - {m['name']} at {m['store']}: ${m['curr']:.2f} ({direction} {abs(float(m['chg'] or 0))}%)"
                )

            ctx_lines.append("")
            ctx_lines.append("Category inflation (week-over-week):")
            for c in cats:
                arrow = "↑" if float(c["wow_pct"] or 0) > 0 else "↓"
                ctx_lines.append(f"  - {c['name']}: {arrow} {abs(float(c['wow_pct'] or 0))}%")

            return "\n".join(ctx_lines)
        except Exception as e:
            logger.error(f"Failed to get price context: {e}")
            return "Price data temporarily unavailable."

    def chat(self, message: str, history: List[Dict]) -> Dict[str, Any]:
        """Generate a response to the user's message."""
        client = self._get_client()

        if not client:
            return self._fallback_response(message)

        price_context = self._get_price_context()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Current SmartCart data:\n{price_context}"},
        ]

        # Add conversation history
        for h in history[-6:]:  # Last 6 messages for context window
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

        messages.append({"role": "user", "content": message})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            answer = response.choices[0].message.content

            return {
                "response": answer,
                "sources": [],
                "suggestions": self._generate_followups(message),
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response(message)

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Rule-based fallback when OpenAI is unavailable."""
        msg_lower = message.lower()

        if "cheap" in msg_lower or "cheapest" in msg_lower or "best price" in msg_lower:
            response = (
                "To find the cheapest prices, check the Price Alerts page — it shows products "
                "near their 90-day lows. You can also use the Basket Optimizer to compare your "
                "shopping list across Woolworths, Coles, and Aldi automatically."
            )
        elif "sale" in msg_lower or "discount" in msg_lower:
            response = (
                "Check the Price Alerts page for current sales. Products marked 'BUY NOW' "
                "are at or near their 90-day price low — these are typically good deals."
            )
        elif "forecast" in msg_lower or "predict" in msg_lower or "going up" in msg_lower:
            response = (
                "Our 30-day price forecasts use XGBoost machine learning trained on historical "
                "price data. Visit the Forecasts page and search for any product to see its "
                "predicted price trend and a 'Buy now or wait' recommendation."
            )
        elif "aldi" in msg_lower or "woolworths" in msg_lower or "coles" in msg_lower:
            response = (
                "Use the Basket Optimizer to compare your shopping list across all three stores. "
                "Generally, Aldi tends to be cheapest for staples, while Woolworths and Coles "
                "have more variety and frequent specials."
            )
        elif "inflation" in msg_lower:
            response = (
                "The Dashboard shows week-over-week inflation by category. Dairy and Produce "
                "typically see the most price volatility. The Analytics page has detailed "
                "category inflation charts."
            )
        else:
            response = (
                "I can help you find the best grocery prices! Try asking about:\n"
                "- 'Which store is cheapest for milk?'\n"
                "- 'What's on sale this week?'\n"
                "- 'Show me price forecasts for eggs'\n"
                "- 'How much can I save at Aldi vs Woolworths?'"
            )

        return {
            "response": response,
            "sources": [],
            "suggestions": self._generate_followups(message),
        }

    def _generate_followups(self, message: str) -> List[str]:
        """Generate contextual follow-up suggestions."""
        suggestions = [
            "What products are on sale right now?",
            "Compare my basket across stores",
            "Show me 30-day price forecasts",
            "Which categories have the biggest inflation?",
        ]
        return suggestions[:3]
