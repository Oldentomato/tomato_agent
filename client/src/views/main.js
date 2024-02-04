import {useState, useEffect, useRef} from 'react'
import {Radio, Button} from 'antd'
import Item from '../components/Item'
import { AnimatePresence } from "framer-motion";
import { SendOutlined } from '@ant-design/icons';
import gptImgLogo from '../assets/bot.jpg'

const req_option = [
    {
        label: "chat",
        value: "chat",
    },
    {
        label: "agent",
        value: "agent",
    }
]

export default function MainView() {
    const msgEnd = useRef();
    const [input, setInput] = useState("");
    const [answer, setAnswer] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [messages, setMessages] = useState([{
        text: "say something!",
        isBot: true
    }])
    const [req, setreq] = useState('chat');



    const FETCH_URL = "http://localhost:8000"

    const onRequestChange = ({ target: { value } }) => {
        setreq(value);
      };

    const handleOnKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSend(); // Enter 입력이 되면 클릭 이벤트 실행
        }
      };

    const handleSend = async(e) =>{
        setIsLoading(true)
        setMessages((prevMessages)=>[
            ...prevMessages,
            {text: input, isBot: false}
        ])

        let response = null

        if(req === "chat"){
            const url = new URL("/llm/chat", FETCH_URL);
            const formData  = new FormData();
            // url.searchParams.append("query", input);
            formData.append("query", input)
            setInput("")
            response = await fetch(url,{
                method: 'POST',
                body: formData
            })

            if (!response.body) throw new Error("No response body");
            const reader = response.body.getReader();
            let temp_str = ""
    
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const text = new TextDecoder("utf-8").decode(value);
                temp_str += text
                setAnswer((prevText) => prevText + text);
            }
            setAnswer("")
            setMessages((prevMessages)=>[
                ...prevMessages,
                {text: temp_str, isBot: true}
            ])
            setIsLoading(false)

            
        }
    }

    useEffect(()=>{
        msgEnd.current.scrollIntoView();

    },[messages])


    return(
        <div>
            <div className="chats">
                <AnimatePresence>
                    {messages.map((message, i)=>
                        <Item key={i}>
                            <div className={message.isBot?"chat bot":"chat"}>
                                {message.isBot ? <img className="chatImg" src={gptImgLogo}/> : <p>You</p> }
                                <p className="txt">{message.text}</p>
                            </div>
                        </Item>)}
                </AnimatePresence>
                {(answer === "" && isLoading) &&
                    <div className="chat bot">
                        <img className="chatImg" src={gptImgLogo} /> <p className="txt">. . .</p>
                    </div>
                }
                {answer !== "" &&
                    <div className="chat bot">
                        <img className="chatImg" src={gptImgLogo} /> <p className="txt">{answer}</p>
                    </div>
                }
                <div ref={msgEnd} />
            </div>
            <div className="chatFooter">
                <Radio.Group optionType="button" buttonStyle="solid" options={req_option} onChange={onRequestChange} value={req} />
                <br />
                <div className="inp">
                    <input type="text" placeholder="Send a message" onKeyDown={handleOnKeyPress} value={input} onChange={(e)=>{setInput(e.target.value)}}/><Button className="send" type="primary" onClick={handleSend} loading={isLoading} icon={<SendOutlined />}/>
                </div>
            </div>
        </div>
    )
}