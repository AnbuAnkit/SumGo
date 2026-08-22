import SendButton from './send-button';
import InputField from './input-field';

function ChatBar(){
    return(
        <div style={{ border: '1px solid blue' }}>
            <InputField /><SendButton />
        </div>
    )
}

export default ChatBar;