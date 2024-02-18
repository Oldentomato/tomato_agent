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
{ path: '/chat/:id', element: <MainView />, withAuthorization: true },
// { path: '/signup', element: <Signup />, withAuthorization: false },
];

const isAuthenticated = localStorage.getItem('token');

const Authorization = ({
  redirectTo,
  children,
}) => {
  if (isAuthenticated) {
    return <>{children}</>;
  } else {
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
                        isAuthenticated={isAuthenticated}
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