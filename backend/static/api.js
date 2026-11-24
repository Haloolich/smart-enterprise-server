
const API_URL = "/api";

// Перевірка авторизації перед відкриттям захищених сторінок
(function checkAuthentication() {
    const currentPath = window.location.pathname;

    const publicPages = ["/login", "/"];

    if (publicPages.includes(currentPath)) {
        return;
    }

    const token = sessionStorage.getItem("accessToken");

    if (!token) {
        window.location.replace("/login");
    }
})();

// Отримання збереженого JWT-токена
function getAccessToken() {
    const token = sessionStorage.getItem("accessToken");

    if (!token) {
        window.location.href = "/login";
        throw new Error("Потрібно авторизуватися");
    }

    return token;
}

// Спільна функція для запитів до API
async function apiFetch(url, options = {}) {
    const token = getAccessToken();

    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${token}`);

    const response = await fetch(url, {
        ...options,
        headers
    });

    // Якщо токен недійсний або прострочений
    if (response.status === 401) {
        sessionStorage.removeItem("accessToken");
        window.location.href = "/login";

        throw new Error("Сесія завершилася. Увійдіть знову.");
    }

    return response;
}
