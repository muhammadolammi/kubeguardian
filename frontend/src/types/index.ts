// src/types/index.ts
export interface User {
    id: string;
    user_name: string;
    email: string;
}

export interface ChatEvent {
    sender: "user" | "agent";
    message: string;
    timestamp?: Date;
}

export interface Session {
    id: string;
    events: ChatEvent[];
    state?: {
        session_title?: string;
        chat_response?: string;
        title?: string;
        [key: string]: any;
    };
    createdAt?: Date;
}

// API response types
export interface ApiContentPart {
    text?: string;
    functionCall?: any;
    functionResponse?: any;
    [key: string]: any;
}

export interface ApiContent {
    parts: ApiContentPart[];
    role?: string;
}

export interface ApiEvent {
    content?: ApiContent;
    invocationId?: string;
    author: string;
    actions?: {
        stateDelta?: any;
        [key: string]: any;
    };
    longRunningToolIds?: string[];
    id?: string;
    timestamp?: number;
    [key: string]: any;
}

export interface ApiSession {
    id: string;
    appName?: string;
    userId?: string;
    state?: {
        session_title?: string;
        chat_response?: string;
        title?: string;
        [key: string]: any;
    };
    events: ApiEvent[];
    createdAt?: string;
    [key: string]: any;
}

export interface ChatMessage {
    content: {
        parts: {
            text: string;
        }[];
    };
}