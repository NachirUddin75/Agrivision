(function () {
    if (!document.querySelector("link[rel~='icon']")) {
        const link = document.createElement("link");
        link.rel = "icon";
        link.type = "image/svg+xml";
        link.href = "favicon.svg";
        document.head.appendChild(link);
    }
})();

const API_BASE_URL = "/api";
async function apiRequest(endpoint, options = {}) {
    const headers = { ...(options.body instanceof FormData ? {} : {"Content-Type":"application/json"}), ...(options.headers || {}) };
    const access = localStorage.getItem("access_token");
    if (access) headers.Authorization = `Bearer ${access}`;
    async function send(h) { return fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers:h }); }
    try {
        let response = await send(headers);
        // Only retry protected endpoints. The refresh endpoint itself cannot recurse.
        if (response.status === 401 && access && endpoint !== "/accounts/token/refresh/") {
            const refresh = localStorage.getItem("refresh_token");
            if (refresh) {
                const renewed = await fetch(`${API_BASE_URL}/accounts/token/refresh/`, {
                    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({refresh})
                });
                if (renewed.ok) {
                    const tokens = await renewed.json();
                    localStorage.setItem("access_token", tokens.access);
                    if (tokens.refresh) localStorage.setItem("refresh_token", tokens.refresh);
                    headers.Authorization = `Bearer ${tokens.access}`;
                    response = await send(headers);
                }
            }
        }
        if (response.status === 401 && access) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user");
        }
        let data = {};
        try { data = await response.json(); } catch {}
        return {ok:response.ok, status:response.status, data};
    } catch (error) {
        console.error("API Error:",error);
        return {ok:false,status:0,data:{message:"Unable to connect to Agrivision server."}};
    }
}