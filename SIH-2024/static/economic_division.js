document.addEventListener("DOMContentLoaded", () => {
    const demographicSelect = document.getElementById("demographic");
    const columnSelect = document.getElementById("column");
    const graphSelect = document.getElementById("graph");
    const generateButton = document.getElementById("generate-btn");
    const summaryDiv = document.getElementById("summary");
    const table = document.getElementById("table");
    const chartCanvas = document.getElementById("chart");

    let chart;

    // Function to generate a random color
    function getRandomColor() {
        return `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.7)`;
    }

    // Function to generate an array of random colors
    function generateColors(count) {
        return Array.from({ length: count }, getRandomColor);
    }

    demographicSelect.addEventListener("change", async () => {
        const selectedDemographic = demographicSelect.value;

        if (selectedDemographic) {
            const response = await fetch("/get_columns_economic_division", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ demographic: selectedDemographic })
            });
            const columns = await response.json();
            columnSelect.innerHTML = columns.map(col => `<option value="${col}">${col}</option>`).join('');
            columnSelect.disabled = false;
        } else {
            columnSelect.innerHTML = '';
            columnSelect.disabled = true;
        }
    });

    generateButton.addEventListener("click", async () => {
        const demographic = demographicSelect.value;
        const column = columnSelect.value;
        const graph = graphSelect.value;

        if (!demographic || !column || !graph) {
            alert("Please select all options.");
            return;
        }

        const response = await fetch("/generate_result_economic_division", {
            method: "POST",
            body: new URLSearchParams({ demographic, column, graph })
        });

        const result = await response.json();

        // Display summary
        summaryDiv.innerHTML = `
            <p>Mean: ${result.summary.mean}</p>
            <p>Sum: ${result.summary.sum}</p>
            <p>Count: ${result.summary.count}</p>
        `;

        // Display table
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Division</th>
                    <th>City/Village Name</th>
                    <th>${column}</th>
                </tr>
            </thead>
            <tbody>
                ${result.data.map(row => `
                    <tr>
                        <td>${row['Division']}</td>
                        <td>${row['City/Village Name']}</td>
                        <td>${row[column]}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        // Generate random colors
        const colors = generateColors(result.graph_data.length);

        // Render graph
        if (chart) chart.destroy();  // Destroy the previous chart if it exists

        chart = new Chart(chartCanvas, {
            type: graph,
            data: {
                labels: result.data.map(row => row['City/Village Name']), // Labels based on Region or any column
                datasets: [{
                    label: column,
                    data: result.graph_data, // Ensure this data is in a valid array format
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace("0.7", "1")), // Higher opacity for borders
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    });
});
