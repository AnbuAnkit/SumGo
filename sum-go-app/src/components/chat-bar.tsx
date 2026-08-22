import SendButton from './send-button';
import InputField from './input-field';
import './chat-bar.css'




function ChatBar(){
    

    return(<>
        

        <div class="chatbar">
            <InputField />
            <SendButton />
        </div>
        </>
    )
}

export default ChatBar;