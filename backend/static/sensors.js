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

// Завантаження показників датчиків
async function loadReadings() {
    try {
        
        const response = await apiFetch(`${API_URL}/readings`);

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

        // Отримуємо останні 20 показників температури
        const temperatureReadings = readings
            .filter(item => item.sensor_type === "temperature")
            .reverse()
            .slice(-20);

        // Оновлюємо графік
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

        // Час останнього оновлення
        document.getElementById("last-update").textContent =
            "Останнє оновлення: " +
            new Date().toLocaleTimeString("uk-UA");

    } catch (error) {
        console.error("Помилка завантаження датчиків:", error);
    }
}

// Перше завантаження
loadReadings();

// Автоматичне оновлення кожні 5 секунд
setInterval(loadReadings, 5000);
