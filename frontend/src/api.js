// backend address (from .env, or localhost:8000 by default)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ask the backend which LLMs it can use: { available: ['gemini', 'openai'], default: 'gemini' }
export async function getProviders() {
  const res = await fetch(`${API_URL}/providers`)
  if (!res.ok) throw new Error('Request failed')
  return res.json()
}

// send one question + the chat history + the chosen LLM to the backend
export async function sendMessage(message, history, provider) {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST', // we send data
    headers: { 'Content-Type': 'application/json' }, // data is JSON
    body: JSON.stringify({ message, history, provider }), // convert the object to JSON text
  })
  if (!res.ok) throw new Error('Request failed') // 4xx / 5xx = error
  return res.json() // { answer, sources: [{ collection, snippet }] }
}