import type { Metadata } from 'next'
import { Space_Grotesk, Inter, VT323 } from 'next/font/google'
import './globals.css'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['300', '400', '500', '600', '700'],
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-body',
  weight: ['300', '400', '500', '600'],
})

const vt323 = VT323({
  subsets: ['latin'],
  variable: '--font-pixel',
  weight: ['400'],
})

export const metadata: Metadata = {
  title: 'Ritika Rana — Data Analyst & Creative Builder',
  description:
    'Portfolio of Ritika Rana — Data Analyst with 5+ years across analytics, BI, engineering, and AI-powered tools. UQ Master of Data Science. Based in Brisbane, Australia.',
  keywords: [
    'Data Analyst',
    'Business Analyst',
    'Python',
    'SQL',
    'Power BI',
    'Tableau',
    'BigQuery',
    'Azure',
    'Brisbane',
    'Portfolio',
    'Data Science',
  ],
  authors: [{ name: 'Ritika Rana' }],
  openGraph: {
    title: 'Ritika Rana — Data Analyst & Creative Builder',
    description: 'Portfolio of Ritika Rana — 5+ years in analytics, BI, and AI.',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${inter.variable} ${vt323.variable} dark`}
    >
      <body className="bg-deep-bg text-slate-200 font-body antialiased overflow-x-hidden">
        {children}
      </body>
    </html>
  )
}
