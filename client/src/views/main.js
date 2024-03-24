import {useState, useEffect, useRef} from 'react'
import {Radio, Button, Layout, Menu, List} from 'antd'
import Item from '../components/Item'
import { AnimatePresence } from "framer-motion";
import { SendOutlined } from '@ant-design/icons';
import gptImgLogo from '../assets/bot.jpg'
import {useNavigate} from "react-router-dom"
import { LogoutOutlined } from '@ant-design/icons';

const {Header} = Layout;
const {Sider} = Layout;

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
    //debug
    const [chatRooms, setChatRooms] = useState([]);
    const [history_url, sethistory_url] = useState("");
    const navigate = useNavigate();
    const msgEnd = useRef();
    const [input, setInput] = useState("");
    const [answer, setAnswer] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [messages, setMessages] = useState([{
        text: "say something!",
        isBot: true
    }])
    const [is_loading, set_is_loading] = useState(false);
    const [req, setreq] = useState('chat');
    const token = localStorage.getItem('token')

    const FETCH_URL = "http://localhost:8000"

    const onRequestChange = ({ target: { value } }) => {
        setreq(value);
    };

    const handleOnKeyPress = (e) => {
        if (e.key === 'Enter' && !isLoading) {
            e.preventDefault();
            setIsLoading(true)
            handleSend(); // Enter 입력이 되면 클릭 이벤트 실행
        }
    };

    const onLogout = async() =>{
        let url = null
        const token = localStorage.getItem('token')
        url = new URL("/db/logout", FETCH_URL);
        const formData  = new FormData();
        formData.append("token", token);
        fetch(url,{
            method: 'POST',
            body: formData
        }).then(response=>{
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // 응답 본문을 JSON으로 파싱
        }).then(data=>{
            if(!data.success){
                window.alert("로그아웃에 실패했습니다.")
            }else{
                window.alert("로그아웃되었습니다.")
                localStorage.setItem('token','')
                navigate('/')
            }
        }).catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    }

    const on_new_chat = () =>{
        sethistory_url("")
        setMessages([{
            text: "say something!",
            isBot: true
        }])
    }

    const get_chatmsgs = async(item) =>{
        if(item.path !== history_url){
            sethistory_url(item.path)
            const url = new URL("/agent/getchat", FETCH_URL);
    
            const formData = new FormData();
            formData.append("chatroom_url", item.path)
            fetch(url, {
                method: 'POST',
                body: formData
            }).then(response=>{
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // 응답 본문을 JSON으로 파싱
            }).then(data=>{
                if(data.success){
                    const datas = data.item.messages
                    const modified_datas = datas.map((e)=>{
                        return {text: e.content, isBot: e.type === "human" ? false : true}
                    })
                    setMessages(modified_datas)
                }
                else{
                    console.log(data)
                }
            }).catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            });
        }
    }
    //fetch요청보내는 부분 중복이 많음 하나의 함수로 만들어서 사용하도록 전체적으로 수정이 필요함
    const new_chat_sql = () =>{
        const formData = new FormData();

        const url = new URL("/db/createchat", FETCH_URL);
        formData.append("token", token)
        formData.append("chat_num", chatRooms.length)
        fetch(url, {
            method: 'POST',
            body: formData
        }).then(response=>{
            if (!response.ok) {
                throw new Error('Network was not ok');
            }
            return response.json(); // 응답 본문을 JSON으로 파싱
        }).then(data=>{
            if(data.success){
                console.log("its ok")
            }
            else{
                console.log(data)
                throw new Error('response was not ok');
            }
        }).catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    }


    const handleSend = async(e) =>{
        setMessages((prevMessages)=>[
            ...prevMessages,
            {text: input, isBot: false}
        ])

        let response = null
        let url = null
        const formData  = new FormData();

        if(req === "chat"){
            url = new URL("/llm/chat", FETCH_URL);
        }else if(req === "agent"){
            url = new URL("/agent/chat", FETCH_URL);
            if(history_url === ""){
                setChatRooms((prev)=>[
                    ...prev,
                    {'id': token+chatRooms.length, 'name': 'Room_'+token+chatRooms.length, 'path': './store/'+token+chatRooms.length+'.json'}
                ])
                formData.append("history_url", './store/'+token+chatRooms.length+'.json')
                formData.append("is_new", true)
                new_chat_sql()
            }
            else{
                formData.append("history_url", history_url)
                formData.append("is_new", false)
            }
        }
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

    const getchats = () =>{
        let url = null
        url = new URL("/db/getchats", FETCH_URL);
        const formData  = new FormData();
        formData.append("token", token);
        fetch(url,{
            method: 'POST',
            mode: 'cors',
            body: formData
        }).then(response=>{
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // 응답 본문을 JSON으로 파싱
        }).then(data=>{
            if(data.success){
                const result_data = data.item.map(item=>{
                    return {'id': item.chat_id, 'name': 'Room_'+item.chat_id, 'path': item.chat_path}
                })
                setChatRooms(result_data)
            }
        }).catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    }

    const logincheck = async() =>{
        //페이지 입장 시 두번 체크함
        //localstorage에 token이 있는가 & token으로 유저정보를 가져오기
        let url = null
        url = new URL("/db/getuser", FETCH_URL);
        const formData  = new FormData();
        formData.append("token", token);
        fetch(url,{
            method: 'POST',
            mode: 'cors',
            body: formData
        }).then(response=>{
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // 응답 본문을 JSON으로 파싱
        }).then(data=>{
            if(!data.success){
                window.alert("잘못된 접근입니다.")
                navigate("/")
            }
            else{
                getchats()
            }
        }).catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    }


    useEffect(()=>{
        logincheck()
    },[])

    useEffect(()=>{
        msgEnd.current.scrollIntoView();

    },[messages, answer])


    return(
        <div>
            <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ color: 'white', marginTop:'10px',fontFamily:"Archivo Black", fontSize: '2.5rem' }}>TOMATO AGENT</div>
                <Button type="text" onClick={onLogout} icon={<LogoutOutlined />} style={{ color: 'white' }}>
                    logout
                </Button>
            </Header>
            <div className="chats">
                <AnimatePresence>
                    {messages.map((message, i)=>
                        <Item key={i}>
                            <div className={message.isBot?"chat bot":"chat"}>
                                {message.isBot ? <img className="chatImg" src={gptImgLogo}/> : <p>You</p> }
                                <p className="txt" style={{whiteSpace:"pre-line", textAlign:'left'}} key={i}>
                                    {message.text.includes("```") ? (
                                        <div>
                                        {message.text.split("```").map((part, index) =>
                                            index % 2 === 0 ? (
                                            <span key={index}>{part}</span>
                                            ) : (
                                            <code style={{backgroundColor:'rgba(0, 0, 0, 0.5)', margin:'10px', color:'rgb(120,120,120)'}} key={index}>{part}</code>
                                            )
                                        )}
                                        </div>
                                    ) : (
                                        message.text
                                    )}
                                </p>
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
                        <img className="chatImg" src={gptImgLogo} /> <p style={{whiteSpace:"pre-line", textAlign:'left'}} className="txt">{answer}</p>
                    </div>
                }
                <div ref={msgEnd} />
            </div>

            <div className='chatList'>
                <Sider width={200} style={{ background: '#fff', borderLeft: '1px solid #f0f0f0' }}>
                    <Menu
                    mode="inline"
                    defaultSelectedKeys={['0']}
                    style={{ height: '100%', borderRight: 0 }}
                    >
                    <List
                        dataSource={chatRooms}
                        renderItem={item => (
                        <List.Item key={item.id} onClick={()=>{
                            get_chatmsgs(item)
                        }}>
                            <List.Item.Meta title={item.name} />
                        </List.Item>
                        )}
                    />
                    </Menu>
                </Sider>
            </div>
            <div className="chatFooter">
                <Radio.Group optionType="button" buttonStyle="solid" options={req_option} onChange={onRequestChange} value={req} />
                <br />
                <div className="inp">
                    <input type="text" placeholder="Send a message" onKeyUp={handleOnKeyPress} value={input} onChange={(e)=>{setInput(e.target.value)}}/><Button className="send" type="primary" onClick={handleSend} loading={isLoading} icon={<SendOutlined />}/>
                </div>
                <Button type="text" onClick={on_new_chat} style={{ color: 'white' }}>
                    new chat
                </Button>
            </div>
        </div>
    )
}