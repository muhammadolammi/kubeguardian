const backendUrl = "http://localhost:8081";
const appName = "chat";

// --- Session helpers ---
function getCurrentSessionId() {
    const path = window.location.pathname.split('/');
    return path[2] || null; // /chat/{session-id}
}

async function getCurrentUser() {
    try {
        const res = await fetch(`${backendUrl}/me`, { credentials: "include" });
        if (!res.ok) return null;
        return await res.json(); // returns { user_id, user_name, email }
    } catch {
        return null;
    }
}

async function fetchSessions(userId) {
    try {
        const res = await fetch(`${backendUrl}/apps/${appName}/users/${userId}/sessions`, {
            credentials: "include"
        });
        return await res.json();
    } catch (err) {
        console.error("Failed to fetch sessions:", err);
        return [];
    }
}

function renderSessions(sessions, userId) {
    const list = document.getElementById("sessionsList");
    list.innerHTML = "";

    // New Chat button
    const newBtn = document.createElement("button");
    newBtn.className = "mb-4 rounded-md bg-[#1172d4] px-3 py-2 text-white hover:bg-[#0d5bab]";
    newBtn.textContent = "+ New Chat";
    newBtn.addEventListener("click", async () => {
        currentSession = await getOrCreateSession(userId, null);
        loadSessionMessages(currentSession);
        fetchAndRenderSessions(userId);
    });
    list.appendChild(newBtn);

    if (!sessions || sessions.length === 0) {
        const p = document.createElement("p");
        p.className = "text-white/50 text-sm";
        p.textContent = "No chat sessions yet.";
        list.appendChild(p);
        return;
    }

    sessions.forEach(session => {
        const div = document.createElement("div");
        div.className = "cursor-pointer rounded-md bg-[#283039] px-3 py-2 text-white hover:bg-[#1172d4]";
        div.textContent = session.id || "Unnamed Session";
        div.addEventListener("click", async () => {
            currentSession = await getOrCreateSession(userId, session.id);
            loadSessionMessages(currentSession);
            window.history.replaceState({}, "", `/chat/${session.id}`);
        });
        list.appendChild(div);
    });
}

async function getOrCreateSession(userId, sessionId = null) {
    try {
        if (sessionId) {
            const res = await fetch(`${backendUrl}/apps/${appName}/users/${userId}/sessions/${sessionId}`, {
                credentials: "include"
            });
            return await res.json();
        } else {
            const res = await fetch(`${backendUrl}/apps/${appName}/users/${userId}/sessions`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ state: {}, events: [] })
            });
            const data = await res.json();
            window.history.replaceState({}, "", `/chat/${data.id}`);
            return data;
        }
    } catch (err) {
        console.error("Session error:", err);
        return null;
    }
}

function loadSessionMessages(session) {
    const chatContainer = document.getElementById("chatContainer");
    chatContainer.innerHTML = "";

    if (!session?.events?.length) return;

    session.events.forEach(event => {
        const msgDiv = document.createElement("div");
        msgDiv.className = event.sender === "user"
            ? "flex items-start justify-end gap-4"
            : "flex items-start gap-4";

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "max-w-md rounded-lg px-4 py-2.5 text-white";
        bubbleDiv.style.backgroundColor = event.sender === "user" ? "#1172d4" : "#283039";
        bubbleDiv.textContent = event.message;

        msgDiv.appendChild(bubbleDiv);
        chatContainer.appendChild(msgDiv);
    });

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage(userId, sessionId, message) {
    try {
        const res = await fetch(`${backendUrl}/run`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                appName,
                userId,
                sessionId,
                newMessage: { content: message },
                streaming: false
            })
        });
        const data = await res.json();
        return data[0]?.content?.parts?.[0]?.text || "";
    } catch (err) {
        console.error("Failed to send message:", err);
        return "";
    }
}

// --- Init ---
let currentSession = null;

async function fetchAndRenderSessions(userId) {
    const sessions = await fetchSessions(userId);
    renderSessions(sessions, userId);
}

document.addEventListener("DOMContentLoaded", async () => {
    const user = await getCurrentUser();
    if (!user?.user_id) {
        window.location.href = "/login";
        return;
    }

    const userId = user.user_id;

    // Sidebar sessions
    await fetchAndRenderSessions(userId);

    // Load current session (persistent)
    const sessionId = getCurrentSessionId();
    currentSession = await getOrCreateSession(userId, sessionId);
    loadSessionMessages(currentSession);

    // Chat send
    const input = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");

    sendBtn.addEventListener("click", async () => {
        const text = input.value.trim();
        if (!text) return;

        if (!currentSession || !currentSession.id) {
            currentSession = await getOrCreateSession(userId, null);
            loadSessionMessages(currentSession);
            await fetchAndRenderSessions(userId);
        }

        currentSession.events.push({ sender: "user", message: text });
        loadSessionMessages(currentSession);
        input.value = "";

        const reply = await sendMessage(userId, currentSession.id, text);
        if (reply) {
            currentSession.events.push({ sender: "agent", message: reply });
            loadSessionMessages(currentSession);
        }
    });

    input.addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });
});
