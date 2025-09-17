import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';

interface AuthContainerProps {
    onAuthSuccess: () => void;
}

const AuthContainer: React.FC<AuthContainerProps> = ({ onAuthSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);

    const switchToRegister = () => setIsLogin(false);
    const switchToLogin = () => setIsLogin(true);

    return isLogin ? (
        <Login
            onSwitchToRegister={switchToRegister}
            onLoginSuccess={onAuthSuccess}
        />
    ) : (
        <Register
            onSwitchToLogin={switchToLogin}
            onRegisterSuccess={onAuthSuccess}
        />
    );
};

export default AuthContainer;