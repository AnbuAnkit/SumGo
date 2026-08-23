import { useState } from "react";

function InputField(){
    const [usertxt, newUsertxt] = useState("")
 return(<div>
    <form>
        {/* <label>Enter text here</label> */}
        <input type="text" placeholder="Enter text here" onChange={()=>{
            newUsertxt(event.target.value)
            console.timeLog(usertxt) 
        }}></input>
    </form>
    </div>
 )
}

export default InputField;