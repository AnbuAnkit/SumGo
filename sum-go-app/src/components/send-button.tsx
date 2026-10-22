type SendButtonProps = {
  disabled?: boolean;
};

function SendButton({ disabled = false }: SendButtonProps) {
  return (
    <button className="send-button" type="submit" disabled={disabled} aria-label="Send message">
      Send
    </button>
  );
}

export default SendButton;
