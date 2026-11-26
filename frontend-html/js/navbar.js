(function () {
    if (!document.querySelector("link[rel~='icon']")) {
        const link = document.createElement("link");
        link.rel = "icon";
        link.type = "image/svg+xml";
        link.href = "favicon.svg";
        document.head.appendChild(link);
    }
})();

document.addEventListener("DOMContentLoaded", function () {
    const isAuthenticated = Boolean(localStorage.getItem("access_token"));

    const authActionsHtml = isAuthenticated
        ? `
            <a href="dashboard.html" class="btn agr-get-started-btn">
                Go to Dashboard →
            </a>
          `
        : `
            <a href="login.html" class="btn agr-login-btn">Login</a>
            <a href="register.html" class="btn agr-get-started-btn">Get Started →</a>
          `;

    const navbar = document.createElement("nav");
    navbar.className = "navbar navbar-expand-lg agr-navbar";
    navbar.innerHTML = `
        <div class="container">
            <a href="home.html" class="navbar-brand d-flex align-items-center gap-2">
                <div class="agr-logo">🌱</div>
                <div>
                    <div class="agr-brand-name">Agrivision</div>
                    <div class="agr-brand-tagline">ANALYZE SOIL. GROW SMARTER.</div>
                </div>
            </a>

            <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#agrNavbarMenu"
                aria-controls="agrNavbarMenu"
                aria-expanded="false"
                aria-label="Toggle navigation"
            >
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="agrNavbarMenu">
                <ul class="navbar-nav mx-auto mb-2 mb-lg-0 gap-lg-2">
                    <li class="nav-item">
                        <a class="nav-link agr-nav-link" href="home.html">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link agr-nav-link" href="home.html#features" data-section="features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link agr-nav-link" href="home.html#how-it-works" data-section="how-it-works">How It Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link agr-nav-link" href="home.html#why-agrivision" data-section="why-agrivision">About</a>
                    </li>
                </ul>

                <div class="d-flex align-items-center gap-2">
                    ${authActionsHtml}
                </div>
            </div>
        </div>
    `;

    document.body.prepend(navbar);

    const currentPage = window.location.pathname.split("/").pop().toLowerCase();

    navbar.querySelectorAll("[data-section]").forEach(function (link) {
        link.addEventListener("click", function (event) {
            const sectionId = this.getAttribute("data-section");
            const target = document.getElementById(sectionId);
            if ((currentPage === "" || currentPage === "home.html") && target) {
                event.preventDefault();
                const targetPosition = target.getBoundingClientRect().top + window.scrollY - navbar.offsetHeight - 12;
                window.scrollTo({ top: targetPosition, behavior: "smooth" });
                history.pushState(null, "", `home.html#${sectionId}`);
            }
        });
    });

    function scrollToHash() {
        const hash = window.location.hash;
        if (!hash) return;
        const target = document.getElementById(hash.substring(1));
        if (!target) return;
        setTimeout(() => {
            const targetPosition = target.getBoundingClientRect().top + window.scrollY - navbar.offsetHeight - 12;
            window.scrollTo({ top: targetPosition, behavior: "smooth" });
        }, 80);
    }

    window.addEventListener("load", scrollToHash);
    window.addEventListener("hashchange", scrollToHash);
});