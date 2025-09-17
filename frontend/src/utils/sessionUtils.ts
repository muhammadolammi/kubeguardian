// src/utils/sessionUtils.ts
import { Session, ApiSession, ChatEvent, ApiEvent, ApiContentPart } from '../types';

// Helper to extract text from API content parts
const extractTextFromParts = (parts: ApiContentPart[]): string => {
    return parts
        .filter(part => part.text && typeof part.text === 'string')
        .map(part => part.text as string)
        .join(' ')
        .trim();
};

// Helper to determine sender type
const getSenderType = (author: string): "user" | "agent" => {
    return author === "user" ? "user" : "agent";
};

export const convertApiSessionToSession = (apiSession: ApiSession): Session => {
    const events: ChatEvent[] = [];

    // Process events from API response
    if (apiSession.events && Array.isArray(apiSession.events)) {
        apiSession.events.forEach((event: ApiEvent) => {
            if (event.content && event.content.parts && event.author) {
                const message = extractTextFromParts(event.content.parts);
                if (message) {
                    events.push({
                        sender: getSenderType(event.author),
                        message: message,
                        timestamp: event.timestamp ? new Date(event.timestamp * 1000) : new Date()
                    });
                }
            }
        });
    }

    // Add AI response from state if it exists and isn't already in events
    if (apiSession.state && apiSession.state.chat_response) {
        const chatResponse = apiSession.state.chat_response;
        const hasResponseInEvents = events.some(event =>
            event.sender === "agent" && event.message.includes(chatResponse)
        );


    }

    return {
        id: apiSession.id,
        state: apiSession.state || {},
        createdAt: apiSession.createdAt ? new Date(apiSession.createdAt) : new Date(),
        events: events
    };
};

// Helper function to get title from session state
export const getSessionTitle = (session: Session): string => {
    // Check for title in session state
    if (session.state && session.state.session_title) {
        return session.state.session_title.toString().trim();
    }

    if (session.state && session.state.title) {
        return session.state.title.toString().trim();
    }

    // Fallback: generate title from first user message
    if (session.state && session.state.chat_response) {
        const firsAgentMessage = session.state.chat_response;

        if (firsAgentMessage) {
            const words = firsAgentMessage.split(/\s+/);
            if (words.length <= 5) {
                return firsAgentMessage;
            }
            return words.slice(0, 5).join(' ') + '...';
        }
    }
    return ""

};