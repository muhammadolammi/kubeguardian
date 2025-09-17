async function logout() {
    await fetch(`${backendurl}/logout`, {
        method: "POST",
        credentials: "include"
    });
    window.location.href = "/login";
}
