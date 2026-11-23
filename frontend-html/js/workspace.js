(function () {
    const NAV_ITEMS = [
        { href: "dashboard.html", label: "Dashboard", icon: "bi-grid-1x2-fill" },
        { href: "soil-analysis.html", label: "Soil Analysis", icon: "bi-droplet-half" },
        { href: "crop-recommendation.html", label: "Crop Recommendation", icon: "bi-flower1" },
        { href: "weather.html", label: "Weather & Irrigation", icon: "bi-cloud-sun-fill" },
        { href: "crop-care.html", label: "Crop Care", icon: "bi-shield-check" },
        { href: "support.html", label: "Support Center", icon: "bi-chat-dots-fill" },
    ];

    document.addEventListener("DOMContentLoaded", function () {
        if (typeof requireAuth === "function") {
            requireAuth();
        }

        const host = document.getElementById("workspace-shell");
        if (!host) return;

        const pageTitle = document.body.dataset.pageTitle || "Workspace";
        const currentPage = (window.location.pathname.split("/").pop() || "dashboard.html").toLowerCase();
        const user = (typeof getCurrentUser === "function" ? getCurrentUser() : null) || {};
        const firstName = user.first_name || user.username || "Farmer";
        const initial = firstName.charAt(0).toUpperCase();
        const email = user.email || "Agrivision User";
        const year = new Date().getFullYear();

        const navLinksHtml = NAV_ITEMS.map((item) => {
            const activeClass = currentPage === item.href ? "active" : "";
            return `
                <a href="${item.href}" class="${activeClass}">
                    <span class="agr-sidebar-icon"><i class="bi ${item.icon}"></i></span>
                    <span>${item.label}</span>
                </a>
            `;
        }).join("");

        const mainContent = document.createElement("div");
        while (host.firstChild) {
            mainContent.appendChild(host.firstChild);
        }

        const shell = document.createElement("div");
        shell.innerHTML = `
            <div id="sidebarOverlay" class="agr-sidebar-overlay"></div>

            <aside id="dashboardSidebar" class="agr-dashboard-sidebar">
                <div class="agr-sidebar-logo">
                    <a href="dashboard.html" class="text-decoration-none d-flex align-items-center gap-3">
                        <div class="agr-dashboard-logo">🌱</div>
                        <div>
                            <div class="agr-dashboard-brand">Agrivision</div>
                            <div class="agr-dashboard-tagline">SMART FARMING</div>
                        </div>
                    </a>
                </div>

                <div class="agr-sidebar-content">
                    <div class="agr-sidebar-section-title">Workspace</div>
                    <nav class="agr-sidebar-nav" aria-label="Workspace navigation">
                        ${navLinksHtml}
                    </nav>

                    <div class="agr-sidebar-section-title account-section">Account</div>
                    <button id="logoutBtn" type="button" class="agr-sidebar-logout">
                        <span class="agr-sidebar-icon"><i class="bi bi-box-arrow-right"></i></span>
                        <span>Logout</span>
                    </button>
                </div>

                <div class="agr-sidebar-user">
                    <div class="agr-user-card">
                        <div id="sidebarAvatar" class="agr-user-avatar"></div>
                        <div class="min-w-0">
                            <div id="sidebarUserName" class="agr-sidebar-user-name"></div>
                            <div id="sidebarUserEmail" class="agr-sidebar-user-email"></div>
                        </div>
                    </div>
                </div>
            </aside>

            <div class="agr-dashboard-main d-flex flex-column min-vh-100">
                <header class="agr-dashboard-header">
                    <div class="container-fluid px-3 px-lg-4">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center gap-3">
                                <button id="sidebarToggle" type="button" class="agr-mobile-menu" aria-label="Toggle menu">
                                    <i class="bi bi-list"></i>
                                </button>
                                <div>
                                    <div class="agr-workspace-label">Agrivision Workspace</div>
                                    <h1 class="agr-dashboard-page-title mb-0">${pageTitle}</h1>
                                </div>
                            </div>

                            <div class="d-flex align-items-center gap-3">
                                <a href="support.html" class="agr-support-btn">
                                    <i class="bi bi-chat-dots"></i>
                                    <span class="d-none d-sm-inline">Support</span>
                                </a>
                                <div class="text-end d-none d-sm-block">
                                    <div id="headerUserName" class="agr-header-user-name"></div>
                                    <div class="agr-header-user-role">Farmer account</div>
                                </div>
                                <div id="headerAvatar" class="agr-header-avatar"></div>
                            </div>
                        </div>
                    </div>
                </header>

                <main class="agr-dashboard-content flex-grow-1">
                    <div class="container-fluid" id="workspace-page-slot"></div>
                </main>

                <footer class="agr-dashboard-footer px-3 px-lg-4">
                    <span>© <span id="dashboardYear">${year}</span> Agrivision. All rights reserved.</span>
                    <span>Analyze Soil. Grow Smarter.</span>
                </footer>
            </div>
        `;

        host.replaceWith(shell);
        const slot = shell.querySelector("#workspace-page-slot");
        while (mainContent.firstChild) {
            slot.appendChild(mainContent.firstChild);
        }

        // Safely populate user text
        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };
        setText("sidebarUserName", firstName);
        setText("sidebarUserEmail", email);
        setText("headerUserName", firstName);
        setText("sidebarAvatar", initial);
        setText("headerAvatar", initial);

        const sidebar = document.getElementById("dashboardSidebar");
        const toggle = document.getElementById("sidebarToggle");
        const overlay = document.getElementById("sidebarOverlay");

        if (sidebar && toggle && overlay) {
            toggle.addEventListener("click", () => {
                sidebar.classList.toggle("show");
                overlay.classList.toggle("show");
            });
            overlay.addEventListener("click", () => {
                sidebar.classList.remove("show");
                overlay.classList.remove("show");
            });
            sidebar.querySelectorAll(".agr-sidebar-nav a").forEach((link) => {
                link.addEventListener("click", () => {
                    sidebar.classList.remove("show");
                    overlay.classList.remove("show");
                });
            });
        }

        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn && typeof logout === "function") {
            logoutBtn.addEventListener("click", logout);
        }
    });
})();
