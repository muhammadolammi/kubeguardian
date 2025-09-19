import React, { useState } from 'react';
import { BACKEND_URL } from "../../const"


interface LoginProps {
    onSwitchToRegister: () => void;
    onLoginSuccess: () => void;
}

const Login: React.FC<LoginProps> = ({ onSwitchToRegister, onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch(`${BACKEND_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
                credentials: "include"
            });

            const data = await response.json();

            if (data.id) {
                alert(`Welcome, ${data.user_name}!`);
                onLoginSuccess();
            } else {
                setError(data.error || "Login failed.");
            }
        } catch (err) {
            console.error("Error:", err);
            setError("Login failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative flex min-h-screen flex-col overflow-x-hidden bg-[#111418] font-['Space_Grotesk',_'Noto_Sans',_sans-serif] text-white">
            <div className="layout-container flex h-full grow flex-col">
                <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3">
                    <div className="flex items-center gap-4">
                        <div className="size-6 text-[#1173d4]">
                            <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                                <path d="M44 4H30.6666V17.3334H17.3334V30.6666H4V44H44V4Z" fill="currentColor"></path>
                            </svg>
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">Kubeguardian</h1>
                    </div>
                </header>
                <main className="flex flex-1 flex-col items-center justify-center py-10 px-4 sm:px-6 lg:px-8">
                    <div className="w-full max-w-md space-y-8 rounded-2xl bg-[#1c2127] p-8 shadow-2xl">
                        <div className="text-center">
                            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
                                Welcome Back
                            </h2>
                            <p className="mt-2 text-sm text-gray-400">
                                Sign in to continue to Kubeguardian
                            </p>
                        </div>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="sr-only" htmlFor="email">Email address</label>
                                <input
                                    autoComplete="email"
                                    className="form-input block w-full resize-none rounded-md border-0 bg-[#283039] p-4 text-white placeholder-gray-500 ring-1 ring-inset ring-[#3b4754] transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[#1173d4] sm:text-sm sm:leading-6"
                                    id="email"
                                    name="email"
                                    placeholder="Enter your email"
                                    required
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                            <div>
                                <label className="sr-only" htmlFor="password">Password</label>
                                <div className="relative">
                                    <input
                                        autoComplete="current-password"
                                        className="form-input block w-full resize-none rounded-md border-0 bg-[#283039] p-4 text-white placeholder-gray-500 ring-1 ring-inset ring-[#3b4754] transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[#1173d4] sm:text-sm sm:leading-6"
                                        id="password"
                                        name="password"
                                        placeholder="Enter your password"
                                        required
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </div>
                            </div>
                            {error && (
                                <div className="text-sm text-red-500">
                                    {error}
                                </div>
                            )}
                            <div className="flex items-center justify-between">
                                <div className="text-sm">
                                    <a className="font-medium text-gray-400 hover:text-[#1173d4]" href="#">
                                        Forgot your password?
                                    </a>
                                </div>
                                <div className="text-sm">
                                    <button
                                        type="button"
                                        className="font-medium text-[#1173d4] hover:text-opacity-80"
                                        onClick={onSwitchToRegister}
                                    >
                                        Create an account
                                    </button>
                                </div>
                            </div>
                            <div>
                                <button
                                    type="submit"
                                    className="flex w-full justify-center rounded-md border border-transparent bg-[#1173d4] py-3 px-4 text-base font-bold text-white shadow-sm transition duration-150 ease-in-out hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-[#1173d4] focus:ring-offset-2 focus:ring-offset-[#1c2127] disabled:opacity-50"
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Logging in...' : 'Log in'}
                                </button>
                            </div>
                        </form>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Login;