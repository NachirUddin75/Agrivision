function saveAuthData(data) {

    if (data.access) {
        localStorage.setItem(
            "access_token",
            data.access
        );
    }

    if (data.refresh) {
        localStorage.setItem(
            "refresh_token",
            data.refresh
        );
    }

    if (data.user) {
        localStorage.setItem(
            "user",
            JSON.stringify(data.user)
        );
    }
}


function getAccessToken() {
    return localStorage.getItem(
        "access_token"
    );
}


function getRefreshToken() {
    return localStorage.getItem(
        "refresh_token"
    );
}


function getCurrentUser() {

    const user =
        localStorage.getItem("user");

    if (!user) {
        return null;
    }

    try {

        return JSON.parse(user);

    } catch {

        return null;
    }
}


function isLoggedIn() {
    return Boolean(
        getAccessToken()
    );
}


function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "refresh_token"
    );

    localStorage.removeItem(
        "user"
    );

    window.location.replace(
        "home.html"
    );
}


function requireAuth() {

    if (!isLoggedIn()) {

        window.location.replace(
            "home.html"
        );
    }
}


/*
 * Prevent browser Back from showing
 * a protected page after logout.
 */

window.addEventListener(
    "pageshow",
    function () {

        if (!isLoggedIn()) {

            const currentPage =
                window.location.pathname
                    .split("/")
                    .pop()
                    .toLowerCase();


            const protectedPages = [
                "dashboard.html",
                "soil-analysis.html",
                "crop-recommendation.html",
                "crop-care.html",
                "weather.html",
                "support.html"
            ];


            if (
                protectedPages.includes(
                    currentPage
                )
            ) {

                window.location.replace(
                    "home.html"
                );
            }
        }

    }
);