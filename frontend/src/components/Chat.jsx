import { useEffect, useRef, useState } from 'react' // React tools
import { getProviders, sendMessage } from '../api' // backend calls (api.js)
import Message from './Message' // one message bubble

// first message shown to the customer
const WELCOME = {
  role: 'assistant',
  content: 'Hi! I can help with orders, delivery, returns and product questions. What do you need?',
}

// names shown on the buttons
const LABELS = { gemini: 'Gemini', openai: 'OpenAI' }

export default function Chat() {
  const [messages, setMessages] = useState([WELCOME]) // all messages in the chat
  const [input, setInput] = useState('') // text in the input box
  const [loading, setLoading] = useState(false) // waiting for the bot?
  const [providers, setProviders] = useState([]) // LLMs the backend can use
  const [provider, setProvider] = useState(null) // LLM chosen by the user
  const bottomRef = useRef(null) // invisible element at the bottom of the chat

  // load the available LLMs once, when the page opens
  useEffect(() => {
    getProviders()
      .then((d) => {
        setProviders(d.available) // buttons to show
        setProvider(d.default) // preselected button
      })
      .catch(() => {}) // backend is off: no buttons, chat still opens
  }, [])

  // scroll down whenever a new message arrives
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend(e) {
    e.preventDefault() // stop the page from reloading
    const text = input.trim() // remove spaces at the start and end
    if (!text || loading) return // ignore empty text or double clicks

    // history for the backend: role + content only, without the welcome message
    const history = messages.slice(1).map(({ role, content }) => ({ role, content }))

    setMessages((m) => [...m, { role: 'user', content: text }]) // show the user message
    setInput('') // clear the input box
    setLoading(true) // show "typing..."

    try {
      const data = await sendMessage(text, history, provider) // ask the backend, with the chosen LLM
      setMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch {
      // backend error: show a friendly message
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false) // hide "typing..."
    }
  }

  return (
    <div className="flex h-[85vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl bg-slate-50 shadow-xl">
      {/* header: title + LLM buttons */}
      <header className="flex items-center justify-between bg-indigo-600 px-4 py-3 text-white">
        <span className="font-semibold">ShopAssist AI</span>

        {providers.length > 1 && ( // show the buttons only when there is a choice
          <div className="flex gap-1 rounded-full bg-indigo-700 p-1 text-xs">
            {providers.map((p) => (
              <button
                key={p}
                onClick={() => setProvider(p)} // select this LLM
                disabled={loading} // do not switch while waiting for an answer
                className={`rounded-full px-3 py-1 transition ${
                  provider === p ? 'bg-white text-indigo-700 font-semibold' : 'text-indigo-100'
                }`}
              >
                {LABELS[p] || p}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* messages area (scrolls) */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <Message key={i} {...m} />
        ))}
        {loading && <p className="text-sm text-slate-400 animate-pulse">ShopAssist is typing...</p>}
        <div ref={bottomRef} />
      </div>

      {/* input box + send button */}
      <form onSubmit={handleSend} className="flex gap-2 border-t border-slate-200 bg-white p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)} // update state on every key press
          placeholder="Ask about orders, returns, products..."
          maxLength={1000}
          className="flex-1 rounded-full border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()} // disabled while waiting or when empty
          className="rounded-full bg-indigo-600 px-5 py-2 text-sm text-white disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  )
}