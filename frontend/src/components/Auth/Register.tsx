import React, { useState } from 'react';

import { BACKEND_URL } from "../../const"

interface RegisterProps {
    onSwitchToLogin: () => void;
    onRegisterSuccess: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSwitchToLogin, onRegisterSuccess }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError("Passwords do not match!");
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            const response = await fetch(`${BACKEND_URL}register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.text();
            alert(data);
            onRegisterSuccess();
        } catch (err) {
            console.error("Error:", err);
            setError("Registration failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative flex h-auto min-h-screen w-full flex-col overflow-x-hidden bg-[#111418] font-['Space_Grotesk',_'Noto_Sans',_sans-serif] text-white">
            <div className="flex h-full grow flex-col">
                <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3">
                    <div className="flex items-center gap-4 text-white">
                        <svg className="h-6 w-6 text-[#1173d4]" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path d="M44 4H30.6666V17.3334H17.3334V30.6666H4V44H44V4Z" fill="currentColor"></path>
                        </svg>
                        <h1 className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">Kubeguardian</h1>
                    </div>
                </header>
                <main className="flex flex-1 items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                    <div className="w-full max-w-md space-y-8">
                        <div className="text-center">
                            <h2 className="mt-6 text-3xl font-bold tracking-tight text-white">Create your account</h2>
                        </div>
                        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
                            <div className="space-y-4 rounded-md shadow-sm">
                                <div>
                                    <label className="sr-only" htmlFor="username">Username</label>
                                    <input
                                        autoComplete="username"
                                        className="relative block w-full appearance-none rounded-md border border-[#3b4754] bg-[#1c2127] px-3 py-3 text-white placeholder-[#9dabb9] focus:z-10 focus:border-[#1173d4] focus:outline-none focus:ring-[#1173d4] sm:text-sm"
                                        id="username"
                                        name="username"
                                        placeholder="Username"
                                        required
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label className="sr-only" htmlFor="email-address">Email address</label>
                                    <input
                                        autoComplete="email"
                                        className="relative block w-full appearance-none rounded-md border border-[#3b4754] bg-[#1c2127] px-3 py-3 text-white placeholder-[#9dabb9] focus:z-10 focus:border-[#1173d4] focus:outline-none focus:ring-[#1173d4] sm:text-sm"
                                        id="email"
                                        name="email"
                                        placeholder="Email address"
                                        required
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label className="sr-only" htmlFor="password">Password</label>
                                    <input
                                        autoComplete="new-password"
                                        className="relative block w-full appearance-none rounded-md border border-[#3b4754] bg-[#1c2127] px-3 py-3 text-white placeholder-[#9dabb9] focus:z-10 focus:border-[#1173d4] focus:outline-none focus:ring-[#1173d4] sm:text-sm"
                                        id="password"
                                        name="password"
                                        placeholder="Password"
                                        required
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </div>
                                <div>
                                    <label className="sr-only" htmlFor="confirm-password">Confirm Password</label>
                                    <input
                                        autoComplete="new-password"
                                        className="relative block w-full appearance-none rounded-md border border-[#3b4754] bg-[#1c2127] px-3 py-3 text-white placeholder-[#9dabb9] focus:z-10 focus:border-[#1173d4] focus:outline-none focus:ring-[#1173d4] sm:text-sm"
                                        id="confirm-password"
                                        name="confirm-password"
                                        placeholder="Confirm Password"
                                        required
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </div>
                            </div>
                            {error && (
                                <div className="text-sm text-red-500">
                                    {error}
                                </div>
                            )}
                            <div>
                                <button
                                    type="submit"
                                    className="group relative flex w-full justify-center rounded-md border border-transparent bg-[#1173d4] py-3 px-4 text-sm font-bold text-white hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-[#1173d4] focus:ring-offset-2 focus:ring-offset-[#111418] disabled:opacity-50"
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Creating account...' : 'Register'}
                                </button>
                            </div>
                            <p className="text-center text-sm text-[#9dabb9]">
                                Already have an account?
                                <button
                                    type="button"
                                    className="ml-1 font-medium text-[#1173d4] hover:text-opacity-80"
                                    onClick={onSwitchToLogin}
                                >
                                    Log in
                                </button>
                            </p>
                        </form>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Register;