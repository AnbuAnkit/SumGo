import { useEffect, useRef, useState } from 'react';
import ChatBar from './components/chat-bar';
import ChatBubble, { type ChatMessage } from './components/chat-bubble';
import './App.css';

const BOT_NAME = 'Sum';
const REPLY_DELAY_MS = 600;

function getBotReply(text: string): string {
  const message = text.trim().toLowerCase();

  if (/^(hi|hey|hello|yo|sup)\b/.test(message)) {
    return 'Hey! How can I help you today?';
  }
  if (/thank/.test(message)) {
    return "You're welcome! Anything else?";
  }
  if (message.endsWith('?')) {
    return "Good question. I'm a placeholder bot for now, so hook me up to an API and I'll answer for real.";
  }
  return `Got it: "${text.trim()}". Tell me more.`;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 0, role: 'bot', text: `Hi, I'm ${BOT_NAME}. Send a message to get started.` },
  ]);
  const [isReplying, setIsReplying] = useState(false);
  const nextId = useRef(1);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isReplying]);

  function handleSend(text: string) {
    const trimmed = text.trim();
    if (trimmed === '' || isReplying) return;

    const userMessage: ChatMessage = { id: nextId.current++, role: 'user', text: trimmed };
    setMessages((previous) => [...previous, userMessage]);
    setIsReplying(true);

    window.setTimeout(() => {
      const botMessage: ChatMessage = {
        id: nextId.current++,
        role: 'bot',
        text: getBotReply(trimmed),
      };
      setMessages((previous) => [...previous, botMessage]);
      setIsReplying(false);
    }, REPLY_DELAY_MS);
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
            <p className="chat-status">{isReplying ? 'typing…' : 'online'}</p>
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
