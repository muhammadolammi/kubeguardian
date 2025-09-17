const backendurl = "http://localhost:8081";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch(`${backendurl}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
                credentials: "include" // important to store cookie
            });

            const data = await response.json();

            if (data.id) {
                alert(`Welcome, ${data.user_name}!`);

                // Redirect to chat page
                window.location.href = "/chat";
            } else {
                alert(data.error || "Login failed.");
            }
        } catch (err) {
            console.error("Error:", err);
            alert("Login failed.");
        }
    });
});
