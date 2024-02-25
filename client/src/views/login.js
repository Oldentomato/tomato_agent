import "../css/login_view.css"
import {useState} from 'react'
import {useNavigate} from "react-router-dom"


export default function LoginView(){
    const [id, set_id] = useState("")
    const [pass, set_pass] = useState("")

    const navigate = useNavigate();

    const FETCH_URL = "http://localhost:8000"

    const generateRandomString = (num) => {
        const characters ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
        let result = '';
        const charactersLength = characters.length;
        for (let i = 0; i < num; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    const onIdChnage = (e) =>{
        set_id(e.target.value)
    }

    const onPassChange = (e) =>{
        set_pass(e.target.value)
    }

    const handleOnKeyPress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            onLoginClick();
        }
    };

    const onLoginClick = async() => {
        if(id !== "" && pass !==""){
            let url = null
            const generate_token = generateRandomString(10)

            localStorage.setItem('token',generate_token);
            url = new URL("/db/login", FETCH_URL);
            const formData  = new FormData();
            formData.append("name", id)
            formData.append("password", pass)
            formData.append("token", generate_token)
            
            fetch(url,{
                method: 'POST',
                body: formData
            }).then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // 응답 본문을 JSON으로 파싱
            })
            .then(data => {
                if(data.success){
                    window.alert(data.item.user_name+"님 환영합니다")
                    navigate("/chat")
                }else{
                    window.alert("로그인에 실패했습니다")
                }

            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            });

            // if (!response.body) throw new Error("No response body");

        }
        else{
            window.alert("id와 password를 모두 입력하십시오")
        }

    }

    return(
        <body className="loginbody">
            <div className="title">
                <h2>TOMATO AGENT</h2>
            </div>
            <div className="container">
                <i style={{'--clr': '#00ff0a'}}></i>
                <i style={{'--clr': '#ff0057'}}></i>
                <i style={{'--clr': '#fffd44'}}></i>
                <div className="login">
                    <h2>LOGIN</h2>
                    <div className="inputBx">
                        <input type="text" onChange={onIdChnage} placeholder="Username"/>
                    </div>
                    <div className="inputBx">
                        <input type="password" onKeyUp={handleOnKeyPress} onChange={onPassChange} placeholder="Password" />
                    </div>
                    <div className="inputBx">
                        <input type="submit" onClick={onLoginClick} value="Sign in" />

                    </div>
                    <div className="links">
                        <a href="#">Sign up</a>
                    </div>
                </div>


            </div>
        </body>

    )
}