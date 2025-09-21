import React, { useState, useEffect, useRef } from 'react';
import { Session, User, ApiSession } from '../../types';
import { convertApiSessionToSession } from '../../utils/sessionUtils';
import { getSessionTitle } from '../../utils/sessionUtils';

import { BACKEND_URL } from "../../const"

const APP_NAME = "chat";

interface ChatProps {
    onLogout: () => void;
}

const Chat: React.FC<ChatProps> = ({ onLogout }) => {
    const [user, setUser] = useState<User | null>(null);
    const [sessions, setSessions] = useState<Session[]>([]);
    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const [isUserLoading, setIsUserLoading] = useState(true);


    useEffect(() => {
        console.log(BACKEND_URL)
        initializeChat();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [currentSession]);

    // Update the initializeChat function
    const initializeChat = async () => {
        try {
            setIsUserLoading(true);
            const userData = await getCurrentUser();
            if (!userData) {
                window.location.href = "/login";
                return;
            }
            setUser(userData);

            const sessionData = await fetchSessions(userData.id);
            console.log("session data: ", sessionData)
            setSessions(sessionData);

            const sessionId = getCurrentSessionId();
            if (sessionId === "") {
                return
            }
            if (sessionId) {
                const session = await getSession(userData.id, sessionId);
                setCurrentSession(session);
                window.history.replaceState({}, "", `/chat/${session.id}`);

            }
        } catch (error) {
            console.error("Failed to initialize chat:", error);
        } finally {
            setIsUserLoading(false);
        }
    };

    const getCurrentUser = async (): Promise<User | null> => {
        try {
            const res = await fetch(`${BACKEND_URL}me`, { credentials: "include" });
            if (!res.ok) return null;
            return await res.json();
        } catch {
            return null;
        }
    };

    const fetchSessions = async (userId: string): Promise<Session[]> => {
        try {
            const res = await fetch(`${BACKEND_URL}apps/${APP_NAME}/users/${userId}/sessions`, {
                credentials: "include"
            });
            const apiSessions: ApiSession[] = await res.json();
            return apiSessions.map(convertApiSessionToSession);
        } catch (err) {
            console.error("Failed to fetch sessions:", err);
            return [];
        }
    };

    const getCurrentSessionId = (): string | null => {
        const path = window.location.pathname.split('/');
        return path[2] || null;
    };

    const getSession = async (userId: string, sessionId: string): Promise<Session> => {
        try {
            const res = await fetch(`${BACKEND_URL}apps/${APP_NAME}/users/${userId}/sessions/${sessionId}`, {
                credentials: "include"
            });
            const apiSession: ApiSession = await res.json();
            const session = convertApiSessionToSession(apiSession);
            return session;

        } catch (err) {
            console.error("Session error:", err);
            throw err;
        }
    };

    const createSession = async (userId: string): Promise<Session> => {
        try {

            const res = await fetch(`${BACKEND_URL}apps/${APP_NAME}/users/${userId}/sessions`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
            });
            const apiSession: ApiSession = await res.json();
            const session = convertApiSessionToSession(apiSession);
            window.history.replaceState({}, "", `/chat/${session.id}`);
            return session;
        }
        catch (err) {
            console.error("Session error:", err);
            throw err;
        }
    };



    // In your Chat component
    const sendMessage = async (userId: string, sessionId: string, message: string): Promise<Session> => {
        try {
            const res = await fetch(`${BACKEND_URL}run`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    appName: APP_NAME,
                    userId,
                    sessionId,
                    newMessage: {
                        parts: [
                            {
                                text: message
                            }
                        ],
                        role: "user"
                    },
                    streaming: false
                })
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                console.error("Server error:", res.status, errorData);
                throw new Error(`Server returned ${res.status}: ${JSON.stringify(errorData)}`);
            }
            const sessiom: Session = await getSession(userId, sessionId);
            return sessiom;

        } catch (err) {
            console.error("Failed to send message:", err);
            throw err;
        }
    };
    const handleSendMessage = async () => {
        if (!message.trim() || !user || isLoading) return;

        setIsLoading(true);
        const text = message.trim();
        setMessage('');

        try {
            // Create session only when sending first message
            let sessionToUse = currentSession;
            let isNewSession = false;

            if (!sessionToUse) {
                sessionToUse = await createSession(user.id);
                setCurrentSession(sessionToUse);
                isNewSession = true;
            }

            // Send message to backend and get the updated session
            const updatedSession = await sendMessage(user.id, sessionToUse.id, text);
            console.log(updatedSession)

            // Update the current session with the backend response
            setCurrentSession(updatedSession);

            // Refresh sessions list to include the updated session
            const updatedSessions = await fetchSessions(user.id);
            setSessions(updatedSessions);

        } catch (error) {
            console.error("Error sending message:", error);

            // Show error message to user
            if (currentSession) {
                const errorSession = {
                    ...currentSession,
                    events: [...currentSession.events, {
                        sender: "agent" as const,
                        message: "Sorry, I encountered an error. Please try again."
                    }]
                };
                setCurrentSession(errorSession);
            }
        } finally {
            setIsLoading(false);
        }
    };
    const handleCreateNewSession = async () => {
        if (!user) return;

        try {
            // Clear current session but don't create a new one until user sends a message
            setCurrentSession(null);
            setMessage('');
            window.history.replaceState({}, "", `/chat`);

            // Refresh sessions list
            const updatedSessions = await fetchSessions(user.id);

            setSessions(updatedSessions);
        } catch (error) {
            console.error("Error preparing new session:", error);
        }
    };

    const handleSelectSession = async (sessionId: string) => {
        if (!user) return;

        try {
            const session = await getSession(user.id, sessionId);
            setCurrentSession(session);
            window.history.replaceState({}, "", `/chat/${session.id}`);

        } catch (error) {
            console.error("Error selecting session:", error);
        }
    };

    const scrollToBottom = () => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleLogout = async () => {
        try {
            await fetch(`${BACKEND_URL}logout`, {
                method: "POST",
                credentials: "include"
            });
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            onLogout();
        }
    };
    const handleDeleteSession = async (sessionId: string) => {
        if (!user) return;

        try {
            await fetch(`${BACKEND_URL}apps/${APP_NAME}/users/${user.id}/sessions/${sessionId}`, {
                method: "DELETE",
                credentials: "include"
            });

            // Refresh sessions list
            const updatedSessions = await fetchSessions(user.id);
            setSessions(updatedSessions);

            // If the deleted session is current, clear it
            if (currentSession?.id === sessionId) {
                setCurrentSession(null);
                window.history.replaceState({}, "", `/chat`);
            }
        } catch (error) {
            console.error("Failed to delete session:", error);
        }
    };
    // Update the conditional rendering at the bottom
    if (isUserLoading) {
        return <div className="flex items-center justify-center h-screen bg-[#111418] text-white">Loading...</div>;
    }

    if (!user) {
        return <div className="flex items-center justify-center h-screen bg-[#111418] text-white">Failed to load user data</div>;
    }



    return (
        <div className="relative flex size-full min-h-screen flex-col bg-[#111418] overflow-x-hidden" style={{ fontFamily: '"Space Grotesk", "Noto Sans", sans-serif' }}>
            <div className="flex h-full grow flex-col">
                <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3">
                    <div className="flex items-center gap-4 text-white">
                        <svg className="size-8 text-[#1173d4]" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path clipRule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" fill="currentColor" fillRule="evenodd"></path>
                        </svg>
                        <h1 className="text-white text-xl font-bold leading-tight tracking-[-0.015em]">KubeGuardian</h1>
                    </div>
                    <div className="flex flex-1 justify-end gap-4">
                        <nav className="flex items-center gap-2">
                            <a className="text-white/80 hover:bg-[#283039] hover:text-white rounded-md px-3 py-2 text-sm font-medium leading-normal transition-colors" href="#">
                                Alerts & Warnings
                            </a>
                            <a className="bg-[#283039] text-white rounded-md px-3 py-2 text-sm font-medium leading-normal" href="#">
                                Chat
                            </a>
                        </nav>
                        <div className="flex items-center gap-4">
                            <button className="flex h-10 w-10 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-[#283039] text-white/80 hover:text-white transition-colors">
                                <span className="material-symbols-outlined text-2xl">notifications</span>
                            </button>
                            <div className="h-10 w-10 shrink-0">
                                <img alt="User avatar" className="h-full w-full rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAYkvNMxplFqcfxOmyYdn2vv_FQersIijLZd1Z0fTq5fIfmMXCjL9jhY8SQ1Fhb7uS4CJ1kL8VlFyoUwqnLJr8ON3kW1NRNl-cVSUCskY95eolpvXUfDQwwMLxZsgrXQtApk9-8uzX6-01Zs6lB14PpCUeLuG9dmrAlcXOz3OeyEs_R2_70pWFvRh55UGAGQ9LCT0lhcld49d7RTNMcRnF67bpEHtle8t58m_gBaqeEWO_A7a0y2mOMOAGHNhfCQiHnuHgHjGkeLQ" />
                            </div>
                            <button
                                onClick={handleLogout}
                                className="text-white/80 hover:text-white rounded-md px-3 py-2 text-sm font-medium leading-normal transition-colors"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </header>
                <main className="flex flex-1 bg-[#1a1e23] px-4 py-8 sm:px-6 lg:px-8">
                    <div className="mx-auto flex w-full max-w-6xl flex-1 gap-4">
                        {/* Sidebar: Sessions */}
                        <div className="flex flex-col w-64 bg-[#111418] rounded-md p-4 overflow-y-auto">
                            <h2 className="text-white text-lg font-semibold mb-4">Chat History</h2>
                            <div className="flex flex-col gap-2">
                                <button
                                    onClick={handleCreateNewSession}
                                    className="mb-4 rounded-md bg-[#1172d4] px-3 py-2 text-white hover:bg-[#0d5bab]"
                                >
                                    + New Chat
                                </button>
                               // In the JSX rendering part:
                                {sessions.map(session => (
                                    <div key={session.id} className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-[#1172d4] bg-[#283039]">
                                        <div
                                            className={`cursor-pointer text-white flex-1 ${currentSession?.id === session.id ? 'font-bold' : ''}`}
                                            onClick={() => handleSelectSession(session.id)}
                                            title={session.id} // Show full ID on hover
                                        >
                                            {getSessionTitle(session)}
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteSession(session.id);
                                            }}
                                            className="ml-2 text-red-500 hover:text-red-700 text-sm"
                                        >
                                            ×
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Chat area */}
                        <div className="flex-1 flex flex-col">
                            <div
                                ref={chatContainerRef}
                                className="flex-1 space-y-6 overflow-y-auto rounded-md bg-[#111418] p-6"
                            >
                                {!currentSession ? (
                                    <div className="flex items-center justify-center h-full">
                                        <div className="text-center text-white/50">
                                            <p className="text-lg mb-2">Start a new conversation</p>
                                            <p className="text-sm">Type a message below to begin chatting</p>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        {currentSession.events.map((event, index) => (
                                            <div
                                                key={index}
                                                className={event.sender === "user"
                                                    ? "flex items-start justify-end gap-4"
                                                    : "flex items-start gap-4"
                                                }
                                            >
                                                <div
                                                    className="max-w-md rounded-lg px-4 py-2.5 text-white"
                                                    style={{ backgroundColor: event.sender === "user" ? "#1172d4" : "#283039" }}
                                                >
                                                    {event.message}
                                                </div>
                                            </div>
                                        ))}
                                        {isLoading && (
                                            <div className="flex items-start gap-4">
                                                <div className="max-w-md rounded-lg px-4 py-2.5 text-white bg-[#283039]">
                                                    Thinking...
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>

                            {/* Input area */}
                            <div className="mt-6 flex items-center gap-4 sticky bottom-0 bg-[#1a1e23] pt-4">
                                <div className="relative flex-1">
                                    <input
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        disabled={isLoading}
                                        className="form-input w-full resize-none rounded-lg border-none bg-[#283039] px-4 py-3 pr-12 text-base text-white placeholder:text-[#9dabb9] focus:outline-none focus:ring-2 focus:ring-[#1172d4] focus:ring-offset-2 focus:ring-offset-[#111418] disabled:opacity-50"
                                        placeholder="Type your message..."
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={isLoading || !message.trim()}
                                        className="absolute bottom-0 right-0 flex h-full w-12 items-center justify-center text-[#9dabb9] hover:text-white disabled:opacity-50"
                                    >
                                        <span className="material-symbols-outlined text-2xl">send</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Chat;