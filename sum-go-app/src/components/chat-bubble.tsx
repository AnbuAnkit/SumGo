export type ChatRole = 'user' | 'bot';

export type ChatMessage = {
  id: number;
  role: ChatRole;
  text: string;
};

type ChatBubbleProps = {
  message: ChatMessage;
};

function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-row ${isUser ? 'from-user' : 'from-bot'}`}>
      <div className={`chat-bubble ${isUser ? 'user' : 'bot'}`}>{message.text}</div>
    </div>
  );
}

export default ChatBubble;
