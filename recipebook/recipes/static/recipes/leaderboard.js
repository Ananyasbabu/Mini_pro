document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/v1/weight-data/")
        .then(response => response.json())
        .then(data => {
            console.log("Received weight data:", data); // Debugging log
            const ctx = document.getElementById('weightChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Weight (kg)',
                        data: data.values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.3,
                        pointBackgroundColor: 'green',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { title: { display: true, text: 'Weight (kg)' } },
                        x: { title: { display: true, text: 'Timeline' } }
                    }
                }
            });
        })
        .catch(error => console.error("Error fetching weight data:", error));
});
