
// Створення бічного меню
async function createMenu() {
    const menuContainer = document.getElementById("sidebar-container");

    if (!menuContainer) return;

    let userRole = null;

    // Отримання ролі поточного користувача
    try {
        const response = await apiFetch("/api/auth/me");

        if (!response.ok) {
            throw new Error("Не вдалося отримати профіль");
        }

        const user = await response.json();
        userRole = user.role;

    } catch (error) {
        console.error("Помилка отримання ролі:", error);
    }

    const isAdmin = userRole === "admin";

    menuContainer.innerHTML = `
        <div class="sidebar-overlay" id="sidebar-overlay"
             onclick="toggleMenu()"></div>

        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h2>Smart Enterprise</h2>
                <button class="menu-close" onclick="toggleMenu()">×</button>
            </div>

            <nav class="sidebar-nav">

                <a href="/dashboard" class="menu-link" data-page="dashboard">
                    <span>⌂</span> Головна
                </a>

                <a href="/static/pages/sensors.html" class="menu-link" data-page="sensors">
                    <span>◉</span> Датчики
                </a>

                <a href="/static/pages/devices.html" class="menu-link" data-page="devices">
                    <span>⚙</span> Пристрої
                </a>

                ${isAdmin ? `
                    <a href="/static/pages/automation.html" class="menu-link" data-page="automation">
                        <span>⟳</span> Автоматизація
                    </a>
                    <a href="/static/pages/users.html" class="menu-link" data-page="users">
                        <span>♙</span> Користувачі
                    </a>
                    <a href="/static/pages/history.html" class="menu-link" data-page="history">
                        <span>◷</span> Історія команд
                    </a>

                    <a href="/static/pages/audit.html" class="menu-link" data-page="audit">
                        <span>▤</span> Журнал аудиту
                    </a>
                ` : ""}

            </nav>

            <div class="sidebar-footer">
                <button class="logout-button" onclick="logout()">
                    <span>↪</span> Вийти
                </button>
            </div>
        </aside>

        <button class="menu-open" onclick="toggleMenu()" aria-label="Відкрити меню">
            ☰
        </button>
    `;

    // Визначення активної сторінки
    const currentPage = window.location.pathname;

    document.querySelectorAll(".menu-link").forEach(link => {
        const href = link.getAttribute("href");

        if (
            (currentPage === "/dashboard" && href === "/dashboard") ||
            currentPage.endsWith(href.replace("/static/pages/", ""))
        ) {
            link.classList.add("active");
        }
    });
}


// Відкриття та закриття меню
function toggleMenu() {
    document.getElementById("sidebar")?.classList.toggle("open");
    document.getElementById("sidebar-overlay")?.classList.toggle("visible");
}


// Вихід з облікового запису
function logout() {
    sessionStorage.removeItem("accessToken");
    window.location.href = "/dashboard";
}


document.addEventListener("DOMContentLoaded", createMenu);
