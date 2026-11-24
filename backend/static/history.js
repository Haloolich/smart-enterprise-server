// Завантаження історії команд
async function loadCommandHistory() {
    try {
        const response = await apiFetch(`${API_URL}/commands/history`);

        if (!response.ok) {
            throw new Error("Не вдалося отримати історію команд");
        }

        const commands = await response.json();

        const tableBody = document.querySelector(
            "#commands-table tbody"
        );

        tableBody.innerHTML = "";

        if (commands.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">Історія команд поки порожня</td>
                </tr>
            `;
        } else {
            commands.forEach(command => {
                const row = document.createElement("tr");

                const values = [
                    command.actuator_name,
                    command.command,
                    command.source,
                    command.result,
                    new Date(command.created_at).toLocaleString("uk-UA")
                ];

                values.forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value ?? "Не вказано";
                    row.appendChild(cell);
                });

                tableBody.appendChild(row);
            });
        }

        document.getElementById("last-update").textContent =
            "Останнє оновлення: " +
            new Date().toLocaleTimeString("uk-UA");

    } catch (error) {
        console.error("Помилка завантаження історії:", error);

        document.querySelector("#commands-table tbody").innerHTML = `
            <tr>
                <td colspan="5">Не вдалося завантажити історію команд</td>
            </tr>
        `;
    }
}

// Перше завантаження
loadCommandHistory();

// Автоматичне оновлення кожні 5 секунд
setInterval(loadCommandHistory, 5000);
