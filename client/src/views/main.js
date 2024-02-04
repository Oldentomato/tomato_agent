import {useState, useEffect, useRef} from 'react'
import {Radio} from 'antd'

const req_option = [
    {
        label: "chat",
        value: "chat"
    },
    {
        label: "agent",
        value: "agent"
    }
]

export default function MainView() {
    const [input, setInput] = useState("");
    const [answer, setAnswer] = useState("");
    const [messages, setMessages] = useState([{
        text: "say something!",
        isBot: true
    }])
    const [req, setreq] = useState('chat');

    return(
        <div>

        </div>
    )
}