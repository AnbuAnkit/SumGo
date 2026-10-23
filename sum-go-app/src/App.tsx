import { useEffect, useRef, useState } from 'react';
import ChatBar from './components/chat-bar';
import ChatBubble, { type ChatMessage } from './components/chat-bubble';
import './App.css';

const BOT_NAME = 'Sum';
const API_BASE = 'http://localhost:8000';

type ChatReplyBody = { reply?: string; detail?: string };

async function requestReply(message: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  const body = (await response.json().catch(() => null)) as ChatReplyBody | null;

  if (!response.ok) {
    throw new Error(body?.detail ?? `Backend responded with ${response.status}`);
  }

  return body?.reply ?? '';
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 0,
      role: 'bot',
      text: `Hi, I'm ${BOT_NAME}. Open the extension on a page, then ask me about it.`,
    },
  ]);
  const [isReplying, setIsReplying] = useState(false);
  const nextId = useRef(1);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isReplying]);

  function addMessage(role: 'user' | 'bot', text: string) {
    setMessages((previous) => [...previous, { id: nextId.current++, role, text }]);
  }

  async function handleSend(text: string) {
    const trimmed = text.trim();
    if (trimmed === '' || isReplying) return;

    addMessage('user', trimmed);
    setIsReplying(true);

    try {
      const reply = await requestReply(trimmed);
      addMessage('bot', reply);
    } catch (error) {
      const reason = error instanceof Error ? error.message : 'Something went wrong.';
      addMessage('bot', `Couldn't get a reply. ${reason}`);
    } finally {
      setIsReplying(false);
    }
  }

  return (
    <main className="chat-app">
      <section className="chat-window">
        <header className="chat-header">
          <span className="chat-avatar" aria-hidden="true">
            {BOT_NAME.charAt(0)}
          </span>
          <div className="chat-identity">
            <h1 className="chat-title">{BOT_NAME}</h1>
            <p className="chat-status">{isReplying ? 'summarizing…' : 'online'}</p>
          </div>
        </header>

        <div className="chat-messages">
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          <div ref={bottomRef} />
        </div>

        <ChatBar onSend={handleSend} disabled={isReplying} />
      </section>
    </main>
  );
}

export default App;
