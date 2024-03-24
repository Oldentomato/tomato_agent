import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
  } from 'react-router-dom';

import MainView from "../views/main"
import LoginView from "../views/login"

const RouterInfo = [
{ path: '/', element: <LoginView />, withAuthorization: false },
{ path: '/chat', element: <MainView />, withAuthorization: true },
// { path: '/signup', element: <Signup />, withAuthorization: false },
];

const Authorization = ({
  redirectTo,
  children,
}) => {
    const isAuthenticated = localStorage.getItem('token');
    if (isAuthenticated) {
        return <>{children}</>;
    } else {
        console.log(isAuthenticated)
        return <Navigate to={redirectTo} />;
    }
};
//취약점이 있음 반대로 채팅방에서 로그인으로 넘어가면 문제없이 로그인화면으로 넘어감
//이 부분은 그냥 지우는 방향으로 생각해볼것
const AutoRouter = () => {
    return (
        <Router>
        <Routes>
            {RouterInfo.map((route) => {
            return (
                <Route
                key={route.path}
                path={route.path}
                element={
                    route.withAuthorization ? (
                    <Authorization
                        redirectTo='/'
                    >
                        {route.element}
                    </Authorization>
                    ) : (
                    route.element
                    )
                }
                />
            );
            })}
        </Routes>
        </Router>
    );
};

export default AutoRouter;