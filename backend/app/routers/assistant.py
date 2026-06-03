"""
AI Assistant router — natural language queries about grocery prices.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.services.ai_assistant import AIAssistant

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[dict]] = []
    suggestions: Optional[List[str]] = []


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message to the AI assistant and get a price-aware response."""
    assistant = AIAssistant(db)
    result = assistant.chat(request.message, request.history or [])
    return ChatResponse(
        response=result["response"],
        sources=result.get("sources", []),
        suggestions=result.get("suggestions", []),
    )


@router.get("/suggestions")
def get_suggestions(db: Session = Depends(get_db)):
    """Get context-aware query suggestions based on current price data."""
    return {
        "suggestions": [
            "Which store has the cheapest milk this week?",
            "What products are on sale right now?",
            "Which categories have had the biggest price increases?",
            "Show me products near their 90-day price low",
            "How much can I save by shopping at Aldi instead of Woolworths?",
            "What are the best value products in the Dairy category?",
            "Are bread prices going up or down?",
            "What's the cheapest way to build a weekly grocery basket?",
        ]
    }
