
const API_URL = "/api";


// Елементи карток датчиків
const sensorElements = {
    temperature: document.getElementById("temperature"),
    humidity: document.getElementById("humidity"),
    gas: document.getElementById("gas"),
    light: document.getElementById("light"),
    motion: document.getElementById("motion")
};


// Створення графіка температури
const chartContext = document
    .getElementById("temperature-chart")
    .getContext("2d");

const temperatureChart = new Chart(chartContext, {
    type: "line",

    data: {
        labels: [],
        datasets: [{
            label: "Температура, °C",
            data: [],
            borderColor: "#2563eb",
            backgroundColor: "rgba(37, 99, 235, 0.1)",
            fill: true,
            tension: 0.3
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: false
            }
        }
    }
});


// Перевірка доступності сервера
async function checkServer() {
    const statusElement =
        document.getElementById("server-status");

    const dot = document.querySelector(".status-dot");

    try {
        const response = await fetch(`${API_URL}/health`);

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


// Отримання показників датчиків
async function loadReadings() {
    try {
        const response = await fetch(`${API_URL}/readings`);

        if (!response.ok) {
            throw new Error("Помилка отримання показників");
        }

        const readings = await response.json();

        const latest = {};

        // Знаходимо останній показник кожного типу
        for (const reading of readings) {
            if (!latest[reading.sensor_type]) {
                latest[reading.sensor_type] = reading;
            }
        }

        // Оновлюємо картки
        for (const [type, element] of Object.entries(sensorElements)) {
            const reading = latest[type];

            if (reading) {
                element.textContent =
                    type === "motion"
                        ? (reading.value === 1 ? "Виявлено" : "Немає")
                        : reading.value;
            }
        }

        // Формуємо дані графіка
        const temperatureReadings = readings
            .filter(item => item.sensor_type === "temperature")
            .reverse()
            .slice(-20);

        temperatureChart.data.labels =
            temperatureReadings.map(item =>
                new Date(item.recorded_at).toLocaleTimeString(
                    "uk-UA",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    }
                )
            );

        temperatureChart.data.datasets[0].data =
            temperatureReadings.map(item => item.value);

        temperatureChart.update();

        document.getElementById("last-update").textContent =
            "Останнє оновлення: " +
            new Date().toLocaleTimeString("uk-UA");

    } catch (error) {
        console.error(error);
    }
}


// Отримання правил автоматизації
async function loadRules() {
    try {
        const response = await fetch(`${API_URL}/rules`);

        if (!response.ok) {
            throw new Error("Помилка отримання правил");
        }

        const rules = await response.json();

        const table = document.getElementById("rules-table");

        table.replaceChildren();

        if (rules.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 5;
            cell.textContent = "Правил поки немає";

            row.appendChild(cell);
            table.appendChild(row);
            return;
        }

        for (const rule of rules) {
            const row = document.createElement("tr");

            const values = [
                rule.name,
                rule.sensor_type,
                `${rule.operator} ${rule.threshold}`,
                rule.action,
                rule.enabled ? "Активне" : "Вимкнене"
            ];

            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }

            row.lastChild.className =
                rule.enabled ? "enabled" : "disabled";

            table.appendChild(row);
        }

    } catch (error) {
        console.error(error);
    }
}


// Отримання журналу подій
async function loadEvents() {
    try {
        const response = await fetch(`${API_URL}/events`);

        if (!response.ok) {
            throw new Error("Помилка отримання подій");
        }

        const events = await response.json();

        const container = document.getElementById("events-list");

        container.replaceChildren();

        if (events.length === 0) {
            const message = document.createElement("p");
            message.textContent = "Автоматичних подій поки немає";
            container.appendChild(message);
            return;
        }

        for (const event of events.slice(0, 10)) {
            const card = document.createElement("div");
            card.className = "event";

            const title = document.createElement("strong");
            title.textContent = event.message;

            const details = document.createElement("p");
            details.textContent =
                `${event.sensor_type}: ${event.value} | ` +
                `${event.action} | ` +
                `${new Date(event.created_at).toLocaleString("uk-UA")}`;

            card.appendChild(title);
            card.appendChild(details);

            container.appendChild(card);
        }

    } catch (error) {
        console.error(error);
    }
}


// Оновлення всієї вебпанелі
async function updateDashboard() {
    await Promise.all([
        checkServer(),
        loadReadings(),
        loadRules(),
        loadEvents()
    ]);
}


// Перше завантаження
updateDashboard();


// Автоматичне оновлення кожні 5 секунд
setInterval(updateDashboard, 5000);
