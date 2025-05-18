document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById('weightChart');
    if (!canvas) {
        console.error("Canvas element with ID 'weightChart' not found.");
        return;
    }

    fetch("/api/v1/weight-data/")
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received weight data:", data);

            // Calculate the min and max values for the y-axis dynamically
            const minWeight = Math.min(...data.weights) - 2; // Optional padding for lower bound
            const maxWeight = Math.max(...data.weights) + 2; // Optional padding for upper bound

            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels, // X-axis labels
                    datasets: [{
                        label: 'Weight (kg)',
                        data: data.weights, // Y-axis data points
                        borderColor: 'rgba(75, 192, 192, 1)', // Line color
                        backgroundColor: 'rgba(75, 192, 192, 0.2)', // Area under line color
                        tension: 0.3, // Smoothing effect on the line
                        pointBackgroundColor: 'green', // Point color
                        pointRadius: 5, // Size of data points
                        fill: true // Fill the area under the line
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    elements: {
                        point: {
                            radius: 5, // Ensure points are visible
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Weight (kg)'
                            },
                            min: minWeight, // Dynamically calculated min value
                            max: maxWeight  // Dynamically calculated max value
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Timeline'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error("Error fetching weight data:", error));
});
