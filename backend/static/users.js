
const USERS_API = "/api/users";

// Завантаження списку користувачів
async function loadUsers() {
    const tableBody = document.querySelector("#users-table tbody");

    try {
        const response = await apiFetch(`${USERS_API}/`);

        if (!response.ok) {
            throw new Error("Не вдалося завантажити користувачів");
        }

        const users = await response.json();

        tableBody.innerHTML = "";

        if (users.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6">Користувачів поки немає</td>
                </tr>
            `;
            return;
        }

        users.forEach(user => {
            const row = document.createElement("tr");

            const roleName = user.role === "admin"
                ? "Адміністратор"
                : "Користувач";

            const statusName = user.is_active
                ? "Активний"
                : "Заблокований";

            const createdAt = user.created_at
                ? new Date(user.created_at).toLocaleString("uk-UA")
                : "Невідомо";

            row.innerHTML = `
                <td>${user.id}</td>
                <td>${escapeHTML(user.username)}</td>
                <td>${roleName}</td>
                <td>
                    <span class="${user.is_active ? "status-active" : "status-blocked"}">
                        ${statusName}
                    </span>
                </td>
                <td>${createdAt}</td>
                <td>
                    <div class="user-actions">

                        <button onclick="changeUserRole(${user.id}, '${user.role}')">
                            Змінити роль
                        </button>

                        <button
                            class="${user.is_active ? "danger-button" : "success-button"}"
                            onclick="changeUserStatus(${user.id}, ${user.is_active})"
                        >
                            ${user.is_active ? "Заблокувати" : "Розблокувати"}
                        </button>
                        
                        <button onclick="changeUserPassword(${user.id}, '${escapeHTML(user.username)}')">
                            Змінити пароль
                        </button>
                    </div>
                </td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">${escapeHTML(error.message)}</td>
            </tr>
        `;
    }
}


// Захист тексту від HTML-вставок
function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[character]);
}


// Створення користувача
document.getElementById("user-create-form").addEventListener("submit", async event => {
    event.preventDefault();

    const message = document.getElementById("create-message");
    const username = document.getElementById("new-username").value.trim();
    const password = document.getElementById("new-password").value;
    const role = document.getElementById("new-role").value;

    try {
        const response = await apiFetch(USERS_API + "/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password,
                role
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося створити користувача");
        }

        message.textContent = "Користувача успішно створено";
        message.style.color = "green";

        event.target.reset();

        await loadUsers();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});


// Зміна ролі користувача
async function changeUserRole(userId, currentRole) {
    const newRole = currentRole === "admin" ? "user" : "admin";

    const confirmed = confirm(
        `Змінити роль користувача на "${newRole}"?`
    );

    if (!confirmed) return;

    try {
        const response = await apiFetch(`${USERS_API}/${userId}/role`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                role: newRole
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося змінити роль");
        }

        alert("Роль користувача успішно змінено");

        await loadUsers();

    } catch (error) {
        alert(error.message);
    }
}


// Блокування або розблокування користувача
async function changeUserStatus(userId, isActive) {
    const newStatus = !isActive;

    const action = newStatus ? "розблокувати" : "заблокувати";

    if (!confirm(`Ви дійсно хочете ${action} цього користувача?`)) {
        return;
    }

    try {
        const response = await apiFetch(`${USERS_API}/${userId}/status`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                is_active: newStatus
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося змінити статус");
        }

        alert("Статус користувача успішно змінено");

        await loadUsers();

    } catch (error) {
        alert(error.message);
    }
}

// Зміна пароля користувача
async function changeUserPassword(userId, username) {
    const newPassword = prompt(
        `Введіть новий пароль для користувача "${username}":`
    );

    if (newPassword === null) return;

    if (newPassword.length < 8 || newPassword.length > 128) {
        alert("Пароль повинен містити від 8 до 128 символів");
        return;
    }

    try {
        const response = await apiFetch(
            `${USERS_API}/${userId}/password`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    password: newPassword
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Не вдалося змінити пароль"
            );
        }

        alert("Пароль користувача успішно змінено");

    } catch (error) {
        alert(error.message);
    }
}

// Завантаження користувачів після відкриття сторінки
document.addEventListener("DOMContentLoaded", loadUsers);
