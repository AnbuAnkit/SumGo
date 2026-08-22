import { useState } from "react";

function SendButton(){
    const [count, newCount] = useState(0)
    
    return(
    <button style={{width:'50px', height:'20px'}} onClick={()=>{
        newCount(count + 1)
    }}>{count}
            {/* <img src='./send-button.jpg' width='50' height='20' />; */}
        </button>
    )
        
    
}

export default SendButton;