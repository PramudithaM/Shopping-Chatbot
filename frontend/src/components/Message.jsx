import { useState } from 'react' // for the "show sources" toggle

export default function Message({ role, content, sources = [] }) {
  const [open, setOpen] = useState(false) // are the sources visible?
  const isUser = role === 'user' // user messages go to the right

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-[85%]">
        {/* the message bubble */}
        <div
          className={`rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap ${
            isUser ? 'bg-indigo-600 text-white' : 'bg-white text-slate-800 shadow-sm'
          }`}
        >
          {content}
        </div>

        {/* sources (only when the bot answer has some) */}
        {sources.length > 0 && (
          <div className="mt-1 text-xs text-slate-500">
            <button onClick={() => setOpen(!open)} className="underline">
              {open ? 'Hide sources' : `Sources (${sources.length})`}
            </button>
            {open && (
              <ul className="mt-1 space-y-1">
                {sources.map((s, i) => (
                  <li key={i} className="rounded bg-slate-50 p-2 border border-slate-200">
                    <span className="font-medium">{s.collection}:</span> {s.snippet}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}