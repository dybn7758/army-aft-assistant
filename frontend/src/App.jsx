import { useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const userId = 1

  const [sessionId] = useState(() => crypto.randomUUID())

  async function sendMessage() {
    if (!message.trim() || loading) {
      return
    }

    const userMessage = message

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: 'user',
        content: userMessage,
      },
    ])

    setMessage('')
    setLoading(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:5000/api/chat',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage,
            user_id: userId,
            session_id: sessionId,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to get a response'
        )
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: data.answer,
        },
      ])
    } catch (error) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      sendMessage()
    }
  }

  return (
    <main className="app">
      <header>
        <h1>Army AFT Assistant</h1>
        <p>
          Ask questions about the Army Fitness Test.
        </p>
      </header>

      <section className="chat">
        {messages.length === 0 && (
          <p className="welcome">
            Ask me a question about the Army AFT.
          </p>
        )}

        {messages.map((chatMessage, index) => (
          <div
            key={index}
            className={`message ${chatMessage.role}`}
          >
            <strong>
              {chatMessage.role === 'user'
                ? 'You'
                : 'AFT Assistant'}
            </strong>

            <p>{chatMessage.content}</p>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <strong>AFT Assistant</strong>
            <p>Thinking...</p>
          </div>
        )}
      </section>

      <section className="input-area">
        <input
          type="text"
          value={message}
          placeholder="Ask an AFT question..."
          onChange={(event) =>
            setMessage(event.target.value)
          }
          onKeyDown={handleKeyDown}
        />

        <button
          type="button"
          onClick={sendMessage}
          disabled={loading}
        >
          Send
        </button>
      </section>
    </main>
  )
}

export default App