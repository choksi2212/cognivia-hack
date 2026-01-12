import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SITARA - Situational Risk Intelligence Platform',
  description: 'An Agentic Situational Risk Intelligence Platform for Women\'s Safety in India',
  keywords: ['safety', 'women safety', 'risk intelligence', 'AI', 'agentic AI', 'India'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
