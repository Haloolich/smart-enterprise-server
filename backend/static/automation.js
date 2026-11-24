// Описи режимів роботи
const modeDescriptions = {
    manual: {
        title: "Ручний режим",
        description: "Керування пристроями здійснюється користувачем. Автоматичні правила не виконуються."
    },
    automatic: {
        title: "Автоматичний режим",
        description: "Система самостійно керує пристроями відповідно до налаштованих правил."
    },
    mixed: {
        title: "Змішаний режим",
        description: "Система виконує автоматичні правила та дозволяє ручне керування пристроями."
    }
};

// Завантаження поточного режиму
async function loadControlMode() {
    try {
        const response = await apiFetch(`${API_URL}/control/mode`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати режим роботи");
        }

        const data = await response.json();

        const modeSelect = document.getElementById("control-mode");
        modeSelect.value = data.control_mode;

        updateModeDescription(data.control_mode);

    } catch (error) {
        console.error("Помилка завантаження режиму:", error);
    }
}

// Оновлення опису режиму
function updateModeDescription(mode) {
    const info = modeDescriptions[mode];

    if (!info) return;

    document.getElementById("control-mode-title").textContent = info.title;
    document.getElementById("control-mode-description").textContent = info.description;
}

// Зміна режиму роботи
async function changeControlMode() {
    const mode = document.getElementById("control-mode").value;
    const message = document.getElementById("mode-message");

    message.textContent = "Збереження режиму...";

    try {
        const response = await apiFetch(`${API_URL}/control/mode`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
        control_mode: mode
    })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося змінити режим");
        }

        updateModeDescription(mode);
        message.textContent = "Режим успішно змінено";

    } catch (error) {
        message.textContent = error.message;
        console.error("Помилка зміни режиму:", error);

        await loadControlMode();
    }
}

// Завантаження правил автоматизації

async function loadRules() {
    try {
        const response = await apiFetch(`${API_URL}/rules`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати правила");
        }

        const rules = await response.json();

        const tableBody = document.querySelector("#rules-table tbody");
        tableBody.innerHTML = "";

        if (rules.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">Правила автоматизації відсутні</td>
                </tr>
            `;
            return;
        }

        const sensorNames = {
            temperature: "Температура",
            humidity: "Вологість",
            gas: "Рівень газу",
            light: "Освітленість",
            motion: "Рух"
        };

        const operatorNames = {
            greater_than: ">",
            less_than: "<",
            equal: "=",
            greater_equal: "≥",
            less_equal: "≤"
        };

        
        const actionNames = {
            turn_on_ventilation: "Увімкнути вентиляцію",
            turn_off_ventilation: "Вимкнути вентиляцію",
            turn_on_lighting: "Увімкнути освітлення",
            turn_off_lighting: "Вимкнути освітлення",
            turn_on_light: "Увімкнути освітлення",
            turn_off_light: "Вимкнути освітлення",
            send_alert: "Надіслати сповіщення"
        };


        rules.forEach(rule => {
            const row = document.createElement("tr");

            const nameCell = document.createElement("td");
            nameCell.textContent = rule.name;

            const conditionCell = document.createElement("td");

            if (rule.sensor_type === "motion") {
                conditionCell.textContent =
                    Number(rule.threshold) === 1
                        ? "Виявлено рух"
                        : "Рух не виявлено";
            } else {
                const sensor = sensorNames[rule.sensor_type] || rule.sensor_type;
                const operator = operatorNames[rule.operator] || rule.operator;

                conditionCell.textContent =
                    `${sensor} ${operator} ${rule.threshold}`;
            }

            const actionCell = document.createElement("td");
            actionCell.textContent =
                actionNames[rule.action] || rule.action;

            const stateCell = document.createElement("td");
            stateCell.textContent = rule.enabled
                ? "Активне"
                : "Вимкнене";

            
            const controlCell = document.createElement("td");

            // Кнопка редагування
            const editButton = document.createElement("button");
            editButton.textContent = "Редагувати";
            editButton.className = "rule-edit-button";
            editButton.addEventListener("click", () => editRule(rule));

            // Кнопка активації
            const toggleButton = document.createElement("button");
            toggleButton.textContent = rule.enabled ? "Вимкнути" : "Увімкнути";
            toggleButton.className = "rule-toggle-button";
            toggleButton.addEventListener("click", () => toggleRule(rule));

            // Кнопка видалення
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Видалити";
            deleteButton.className = "rule-delete-button";
            deleteButton.addEventListener("click", () => deleteRule(rule));

            controlCell.append(editButton, toggleButton, deleteButton);


            row.append(
                nameCell,
                conditionCell,
                actionCell,
                stateCell,
                controlCell
            );

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Помилка завантаження правил:", error);
    }
}


// Завантаження подій автоматизації

async function loadEvents() {
    try {
        const response = await apiFetch(`${API_URL}/events`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати події");
        }

        const events = await response.json();

        const eventsList = document.getElementById("events-list");
        eventsList.innerHTML = "";

        if (events.length === 0) {
            eventsList.textContent = "Події автоматизації відсутні";
            return;
        }

        events.forEach(event => {
            const item = document.createElement("div");
            item.className = "event-item";

            const eventDate = new Date(event.created_at);
            const formattedDate = eventDate.toLocaleString("uk-UA");

            item.textContent =
                `${formattedDate} | ${event.message}`;

            eventsList.appendChild(item);
        });

    } catch (error) {
        console.error("Помилка завантаження подій:", error);

        document.getElementById("events-list").textContent =
            "Не вдалося завантажити події автоматизації";
    }
}


// Обробник зміни режиму
document.getElementById("control-mode")
    .addEventListener("change", changeControlMode);

// Початкове завантаження
loadControlMode();
loadRules();
loadEvents();

// Оновлення інформації кожні 5 секунд
setInterval(() => {
    loadRules();
    loadEvents();
}, 5000);


// Створення нового правила автоматизації

const ruleSensor = document.getElementById("rule-sensor");
const operatorGroup = document.getElementById("operator-group");
const thresholdGroup = document.getElementById("threshold-group");
const motionGroup = document.getElementById("motion-group");

const thresholdInput = document.getElementById("rule-threshold");
const motionSelect = document.getElementById("rule-motion-state");
const operatorSelect = document.getElementById("rule-operator");

// Зміна полів залежно від обраного датчика
function updateRuleSensorFields() {
    const isMotion = ruleSensor.value === "motion";

    operatorGroup.hidden = isMotion;
    thresholdGroup.hidden = isMotion;
    motionGroup.hidden = !isMotion;

    thresholdInput.required = !isMotion;
    motionSelect.required = isMotion;

    if (isMotion) {
        operatorSelect.value = "equal";
    }
}

ruleSensor.addEventListener("change", updateRuleSensorFields);

updateRuleSensorFields();

// Створення нового правила автоматизації
document.getElementById("rule-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const message = document.getElementById("rule-message");
    message.textContent = "Збереження правила...";

    const isMotion = ruleSensor.value === "motion";

    const ruleData = {
        name: document.getElementById("rule-name").value.trim(),
        sensor_type: ruleSensor.value,
        operator: isMotion ? "equal" : operatorSelect.value,
        threshold: isMotion
            ? Number(motionSelect.value)
            : Number(thresholdInput.value),
        action: document.getElementById("rule-action").value,
        description: document.getElementById("rule-description").value.trim() || null
    };

    try {
        const response = await apiFetch(`${API_URL}/rules`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ruleData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося створити правило");
        }

        message.textContent = "Правило успішно створено!";
        this.reset();

        updateRuleSensorFields();
        await loadRules();

    } catch (error) {
        message.textContent = error.message;
        console.error("Помилка створення правила:", error);
    }
});


// Увімкнення або вимкнення правила
async function toggleRule(rule) {
    try {
        const response = await apiFetch(`${API_URL}/rules/${rule.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                enabled: !rule.enabled
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося змінити стан правила");
        }

        await loadRules();

    } catch (error) {
        alert(error.message);
        console.error("Помилка зміни стану правила:", error);
    }
}


// Редагування правила автоматизації
async function editRule(rule) {
    const newName = prompt("Назва правила:", rule.name);

    if (newName === null) return;

    if (!newName.trim()) {
        alert("Назва правила не може бути порожньою");
        return;
    }

    const sensorNames = {
        temperature: "Температура",
        humidity: "Вологість",
        gas: "Рівень газу",
        light: "Освітленість",
        motion: "Рух"
    };

    const newThreshold = prompt(
        rule.sensor_type === "motion"
            ? "Стан руху: 1 — виявлено, 0 — не виявлено"
            : `Нове порогове значення для датчика «${sensorNames[rule.sensor_type] || rule.sensor_type}»:`,
        rule.threshold
    );

    if (newThreshold === null) return;

    const threshold = Number(newThreshold);

    if (
        newThreshold.trim() === "" ||
        !Number.isFinite(threshold)
    ) {
        alert("Введіть коректне числове значення");
        return;
    }

    if (rule.sensor_type === "motion" && ![0, 1].includes(threshold)) {
        alert("Для датчика руху можна використовувати тільки 0 або 1");
        return;
    }

    const newDescription = prompt(
        "Опис правила:",
        rule.description || ""
    );

    if (newDescription === null) return;

    try {
        const response = await apiFetch(`${API_URL}/rules/${rule.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: newName.trim(),
                threshold: threshold,
                description: newDescription.trim() || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося змінити правило");
        }

        await loadRules();

        alert("Правило успішно оновлено!");

    } catch (error) {
        alert(error.message);
        console.error("Помилка редагування правила:", error);
    }
}


// Видалення правила автоматизації
async function deleteRule(rule) {
    const confirmed = confirm(
        `Ви дійсно хочете видалити правило "${rule.name}"?`
    );

    if (!confirmed) return;

    try {
        const response = await apiFetch(`${API_URL}/rules/${rule.id}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Не вдалося видалити правило");
        }

        await loadRules();

        alert("Правило успішно видалено!");

    } catch (error) {
        alert(error.message);
        console.error("Помилка видалення правила:", error);
    }
}
