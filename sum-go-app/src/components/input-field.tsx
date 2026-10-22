type InputFieldProps = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

function InputField({ value, onChange, disabled = false }: InputFieldProps) {
  return (
    <input
      className="chat-input"
      type="text"
      value={value}
      placeholder="Type a message…"
      aria-label="Message"
      autoComplete="off"
      disabled={disabled}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

export default InputField;
