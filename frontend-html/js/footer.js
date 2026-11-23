document.addEventListener("DOMContentLoaded", function () {
    const footerContainer = document.getElementById("footer-container");
    if (!footerContainer) return;

    const currentYear = new Date().getFullYear();

    footerContainer.innerHTML = `
        <footer style="background: #072417; color: #ffffff;" class="mt-auto">
            <div class="container py-5">
                <div class="row g-4 justify-content-between">
                    <div class="col-lg-5">
                        <a href="home.html" class="text-decoration-none d-inline-flex align-items-center gap-3">
                            <div class="agr-logo">🌱</div>
                            <div>
                                <div class="h5 fw-bold text-white mb-0">Agrivision</div>
                                <div class="text-uppercase fw-semibold" style="font-size: 9px; letter-spacing: 0.18em; color: rgba(134, 239, 172, 0.7);">
                                    Analyze Soil. Grow Smarter.
                                </div>
                            </div>
                        </a>
                        <p class="small lh-lg mt-3 mb-0" style="max-width: 420px; color: rgba(220, 252, 231, 0.65);">
                            Soil screening, rule-based crop suitability, live Open-Meteo weather forecasts,
                            and Google Gemini educational guidance in one simple workspace.
                        </p>
                    </div>

                    <div class="col-6 col-md-3 col-lg-2">
                        <h3 class="h6 fw-bold text-white mb-3">Explore</h3>
                        <ul class="list-unstyled d-flex flex-column gap-2 mb-0 small">
                            <li><a href="home.html" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Home</a></li>
                            <li><a href="home.html#features" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Features</a></li>
                            <li><a href="home.html#how-it-works" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">How It Works</a></li>
                            <li><a href="home.html#why-agrivision" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">About</a></li>
                        </ul>
                    </div>

                    <div class="col-6 col-md-3 col-lg-2">
                        <h3 class="h6 fw-bold text-white mb-3">Account</h3>
                        <ul class="list-unstyled d-flex flex-column gap-2 mb-0 small">
                            <li><a href="login.html" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Login</a></li>
                            <li><a href="register.html" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Register</a></li>
                            <li><a href="dashboard.html" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Dashboard</a></li>
                            <li><a href="support.html" class="text-decoration-none" style="color: rgba(220, 252, 231, 0.7);">Support</a></li>
                        </ul>
                    </div>
                </div>

                <div class="border-top mt-5 pt-4 d-flex flex-column flex-md-row justify-content-between gap-2 small" style="border-color: rgba(255,255,255,0.1) !important; color: rgba(220, 252, 231, 0.55);">
                    <span>© ${currentYear} Agrivision. All rights reserved.</span>
                    <span>Smart Farming • Soil Intelligence • Gemini AI</span>
                </div>
            </div>
        </footer>
    `;
});