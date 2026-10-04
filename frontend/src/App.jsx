import Chat from './components/Chat' // the chat window

export default function App() {
  return (
    // full screen, grey background, chat window in the center
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <Chat />
    </div>
  )
}