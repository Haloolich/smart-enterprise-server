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

// Надсилання команди пристрою
async function controlActuator(actuatorId, command) {
    const messageElement = document.getElementById("actuator-message");

    messageElement.textContent = "Надсилання команди...";

    try {
        const response = await apiFetch(
    `${API_URL}/actuators/${actuatorId}/command`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    command: command
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Помилка керування пристроєм");
        }

        messageElement.textContent =
            `Команду для ${data.actuator_code} оброблено успішно`;

        await loadActuators();

    } catch (error) {
        messageElement.textContent = error.message;
        console.error("Помилка керування:", error);
    }
}

// Перше завантаження станів
loadActuators();

// Оновлення кожні 5 секунд
setInterval(loadActuators, 5000);
