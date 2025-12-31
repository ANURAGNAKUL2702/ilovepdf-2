import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PDF Editor - Professional PDF Editing Tool',
  description: 'Edit PDFs with precision - select text, correct spelling, and insert new content while preserving layout',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
