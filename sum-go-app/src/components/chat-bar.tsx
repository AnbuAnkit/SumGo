import { useState, type FormEvent } from 'react';
import SendButton from './send-button';
import InputField from './input-field';
import './chat-bar.css';

type ChatBarProps = {
  onSend: (text: string) => void;
  disabled?: boolean;
};

function ChatBar({ onSend, disabled = false }: ChatBarProps) {
  const [text, setText] = useState('');

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (disabled || text.trim() === '') return;
    onSend(text);
    setText('');
  }

  return (
    <form className="chatbar" onSubmit={handleSubmit}>
      <InputField value={text} onChange={setText} disabled={disabled} />
      <SendButton disabled={disabled || text.trim() === ''} />
    </form>
  );
}

export default ChatBar;
