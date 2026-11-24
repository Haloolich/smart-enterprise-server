// Елементи карток датчиків
const sensorElements = {
    temperature: document.getElementById("temperature"),
    humidity: document.getElementById("humidity"),
    gas: document.getElementById("gas"),
    light: document.getElementById("light"),
    motion: document.getElementById("motion")
};

// Назви та описи режимів
const modeDescriptions = {
    manual: {
        title: "Ручний режим",
        description: "Автоматичне виконання правил вимкнене. Керування пристроями здійснюється користувачем."
    },
    automatic: {
        title: "Автоматичний режим",
        description: "Сервер самостійно перевіряє показники та виконує правила автоматизації."
    },
    mixed: {
        title: "Змішаний режим",
        description: "Автоматизація працює, а користувач може вручну змінювати стан пристроїв."
    }
};


// Перевірка доступності сервера
async function checkServer() {
    const statusElement = document.getElementById("server-status");
    const dot = document.getElementById("status-dot");

    try {
        const response = await apiFetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("Сервер недоступний");
        }

        statusElement.textContent = "Сервер онлайн";
        dot.style.background = "#22c55e";

    } catch (error) {
        statusElement.textContent = "Сервер недоступний";
        dot.style.background = "#dc2626";
    }
}


// Завантаження показників датчиків
async function loadReadings() {
    try {
        const response = await apiFetch(`${API_URL}/readings`);

        if (!response.ok) {
            throw new Error("Помилка отримання показників");
        }

        const readings = await response.json();

        const latest = {};

        // Отримуємо останній показник кожного типу
        for (const reading of readings) {
            if (!latest[reading.sensor_type]) {
                latest[reading.sensor_type] = reading;
            }
        }

        // Оновлюємо картки датчиків
        for (const [type, element] of Object.entries(sensorElements)) {
            const reading = latest[type];

            if (reading) {
                element.textContent =
                    type === "motion"
                        ? (reading.value === 1 ? "Виявлено" : "Немає")
                        : reading.value;
            }
        }

    } catch (error) {
        console.error("Помилка завантаження датчиків:", error);
    }
}


// Завантаження режиму роботи
async function loadControlMode() {
    try {
        const response = await apiFetch(`${API_URL}/control/mode`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати режим роботи");
        }

        const data = await response.json();

        updateModeDescription(data.control_mode);

    } catch (error) {
        console.error("Помилка завантаження режиму:", error);

        document.getElementById("control-mode-title").textContent =
            "Режим недоступний";

        document.getElementById("control-mode-description").textContent =
            "Не вдалося отримати налаштування системи";
    }
}


// Відображення режиму роботи
function updateModeDescription(mode) {
    const info = modeDescriptions[mode];

    if (!info) return;

    document.getElementById("control-mode-title").textContent =
        info.title;

    document.getElementById("control-mode-description").textContent =
        info.description;
}


// Завантаження станів виконавчих пристроїв
async function loadActuators() {
    try {
        const response = await apiFetch(`${API_URL}/actuators`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати пристрої");
        }

        const actuators = await response.json();

        actuators.forEach(actuator => {
            let stateElement = null;

            if (actuator.code === "VENTILATION_01") {
                stateElement = document.getElementById("ventilation-state");
            }

            if (actuator.code === "LIGHT_01") {
                stateElement = document.getElementById("lighting-state");
            }

            if (!stateElement) return;

            if (actuator.state === "on") {
                stateElement.textContent = "Увімкнено";
                stateElement.className = "actuator-state enabled";
            } else {
                stateElement.textContent = "Вимкнено";
                stateElement.className = "actuator-state disabled";
            }
        });

    } catch (error) {
        console.error("Помилка завантаження пристроїв:", error);
    }
}


// Оновлення часу останнього оновлення
function updateLastUpdate() {
    document.getElementById("last-update").textContent =
        "Останнє оновлення: " +
        new Date().toLocaleTimeString("uk-UA");
}


// Оновлення головної сторінки
async function updateDashboard() {
    await Promise.all([
        checkServer(),
        loadReadings(),
        loadControlMode(),
        loadActuators()
    ]);

    updateLastUpdate();
}


// Перше завантаження
updateDashboard();

// Автоматичне оновлення кожні 5 секунд
setInterval(updateDashboard, 5000);
