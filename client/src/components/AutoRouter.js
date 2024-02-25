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