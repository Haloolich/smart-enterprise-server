
const auditTableBody = document.querySelector(
    "#audit-table tbody"
);

const auditStatus = document.getElementById(
    "audit-status"
);

const refreshButton = document.getElementById(
    "refresh-audit"
);


// Переклад типів дій
function getActionName(action) {
    const actions = {
        create_rule: "Створення правила",
        update_rule: "Редагування правила",
        delete_rule: "Видалення правила",
        change_control_mode: "Зміна режиму керування"
    };

    return actions[action] || action;
}


// Форматування дати
function formatDate(dateString) {
    return new Date(dateString).toLocaleString("uk-UA");
}


// Завантаження журналу аудиту
async function loadAuditLogs() {
    try {
        auditStatus.textContent = "Завантаження записів...";

        const response = await apiFetch("/api/audit");

        if (!response.ok) {
            throw new Error("Не вдалося завантажити журнал аудиту");
        }

        const logs = await response.json();

        auditTableBody.innerHTML = "";

        if (logs.length === 0) {
            auditStatus.textContent = "Записів поки немає";
            return;
        }

        logs.forEach(log => {
            const row = document.createElement("tr");

            const values = [
                log.id,
                formatDate(log.created_at),
                getActionName(log.action),
                log.entity_type || "-",
                log.entity_id ?? "-",
                log.description
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            auditTableBody.appendChild(row);
        });

        auditStatus.textContent =
            `Завантажено записів: ${logs.length}`;

    } catch (error) {
        console.error("Помилка журналу аудиту:", error);

        auditStatus.textContent =
            "Помилка завантаження журналу аудиту";
    }
}


// Кнопка оновлення
refreshButton.addEventListener(
    "click",
    loadAuditLogs
);


// Початкове завантаження
loadAuditLogs();
