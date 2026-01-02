import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'StaticWaves AI Control Panel',
  description: 'AI Agent orchestration dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <style>{`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
          }

          a {
            color: #3b82f6;
            text-decoration: none;
          }

          a:hover {
            text-decoration: underline;
          }

          button {
            cursor: pointer;
            font-family: inherit;
          }

          pre {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9rem;
          }

          code {
            background: #1a1a1a;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
          }

          .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
          }

          .card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
          }

          .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.2s;
          }

          .btn-primary {
            background: #3b82f6;
            color: white;
          }

          .btn-primary:hover {
            background: #2563eb;
          }

          .btn-secondary {
            background: #374151;
            color: white;
          }

          .btn-secondary:hover {
            background: #4b5563;
          }

          input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #e0e0e0;
            font-size: 1rem;
            font-family: inherit;
          }

          textarea {
            resize: vertical;
            min-height: 100px;
          }

          label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
          }

          .nav {
            background: #1a1a1a;
            border-bottom: 1px solid #333;
            padding: 1rem 2rem;
            margin-bottom: 2rem;
          }

          .nav ul {
            list-style: none;
            display: flex;
            gap: 2rem;
            align-items: center;
          }

          .nav a {
            color: #9ca3af;
          }

          .nav a:hover {
            color: #e0e0e0;
            text-decoration: none;
          }

          .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 500;
          }

          .badge-green {
            background: #10b981;
            color: white;
          }

          .badge-yellow {
            background: #f59e0b;
            color: white;
          }

          .badge-red {
            background: #ef4444;
            color: white;
          }

          .badge-blue {
            background: #3b82f6;
            color: white;
          }

          .loading {
            text-align: center;
            padding: 2rem;
            color: #9ca3af;
          }

          .error {
            background: #7f1d1d;
            border: 1px solid #991b1b;
            color: #fecaca;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
          }

          .success {
            background: #064e3b;
            border: 1px solid #065f46;
            color: #6ee7b7;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
          }
        `}</style>
      </head>
      <body>
        <nav className="nav">
          <ul>
            <li><strong>🧠 StaticWaves AI</strong></li>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/agents">Agents</a></li>
            <li><a href="/memory">Memory</a></li>
            <li><a href="/episodes">Episodes</a></li>
          </ul>
        </nav>
        {children}
      </body>
    </html>
  )
}
