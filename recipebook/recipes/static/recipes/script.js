function submitBMI(height, weight,bmi) {
    fetch("/api/v1/leaderboard/submit-bmi/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken(),
        },
        body: `height=${encodeURIComponent(height * 100)}&weight=${encodeURIComponent(weight)}`
    })
    .then(response => {
        console.log("🔍 Response status:", response.status);
        return response.json();
    })
    .then(data => {
        if (data.bmi && data.category) {
            console.log(`✅ BMI: ${data.bmi}, Category: ${data.category}`);
            // Optionally update UI
        } else if (data.error) {
            console.error("⚠️ Error:", data.error);
            // Optionally display to user
        }
    })
    .catch(error => console.error("❌ Fetch Error:", error));
}

function calculateBMI() {
    const heightElement = document.getElementById("height");
    const weightElement = document.getElementById("weight");
    const resultElement = document.getElementById("bmiResult");
    const suggestionElement = document.getElementById("foodSuggestion");

    if (!heightElement || !weightElement || !resultElement || !suggestionElement) {
        console.error("One or more elements missing!");
        return;
    }

    const height = parseFloat(heightElement.value) / 100;
    const weight = parseFloat(weightElement.value);

    if (isNaN(height) || isNaN(weight) || height <= 0 || weight <= 0) {
        resultElement.innerHTML = "Please enter valid height and weight!";
        return;
    }

    const bmi = weight / (height * height);
    let category = "";

    if (bmi < 18.5) category = "Underweight";
    else if (bmi < 25) category = "Normal";
    else if (bmi < 30) category = "Overweight";
    else category = "Obese";

    resultElement.innerHTML = `Your BMI is ${bmi.toFixed(2)} (${category})`;

    let foods = {
        "Underweight": ["Banana smoothie", "Dry fruits", "Egg sandwich"],
        "Normal": ["Grilled veggies", "Quinoa salad", "Fruits bowl"],
        "Overweight": ["Steamed broccoli", "Lentil soup", "Green tea"],
        "Obese": ["Cucumber salad", "Oats with fruits", "Boiled veggies"]
    };

    suggestionElement.innerHTML =
        "<strong>Suggested Foods:</strong> <ul>" +
        foods[category].map(item => `<li>${item}</li>`).join('') + "</ul>";

    // ✅ Send BMI data to Django for tracking
    submitBMI(height, weight, bmi);
}



// function updateWeightChart() {
//     fetch("/api/v1/weight-data/")
//     .then(response => response.json())
//     .then(data => {
//         const ctx = document.getElementById('weightChart').getContext('2d');
//         new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: data.labels,
//                 datasets: [{
//                     label: 'Weight (kg)',
//                     data: data.values,
//                     borderColor: 'rgba(75, 192, 192, 1)',
//                     backgroundColor: 'rgba(75, 192, 192, 0.2)',
//                     tension: 0.3,
//                     pointBackgroundColor: 'green',
//                     fill: true
//                 }]
//             },
//             options: {
//                 scales: {
//                     y: {
//                         beginAtZero: false,
//                         title: {
//                             display: true,
//                             text: 'Weight (kg)'
//                         }
//                     },
//                     x: {
//                         title: {
//                             display: true,
//                             text: 'Timeline'
//                         }
//                     }
//                 },
//                 plugins: {
//                     legend: {
//                         display: true
//                     },
//                     tooltip: {
//                         mode: 'index',
//                         intersect: false
//                     }
//                 },
//                 responsive: true
//             }
//         });
//     });
// }
// function updateWeightChart() {
//     fetch("/api/v1/weight-data/")
//     .then(response => {
//         if (!response.ok) {
//             throw new Error("Failed to fetch weight data");
//         }
//         return response.json();
//     })
//     .then(data => {
//         const canvas = document.getElementById('weightChart');
//         if (!canvas) {
//             console.error("❌ Canvas element with ID 'weightChart' not found.");
//             return;
//         }

//         const ctx = canvas.getContext('2d');

//         new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: data.labels, // Dates
//                 datasets: [{
//                     label: 'Weight (kg)',
//                     data: data.weights,  // ✅ Replaced `values` with `weights`
//                     borderColor: 'rgba(75, 192, 192, 1)',
//                     backgroundColor: 'rgba(75, 192, 192, 0.2)',
//                     tension: 0.3,
//                     pointBackgroundColor: 'green',
//                     fill: true
//                 }]
//             },
//             options: {
//                 scales: {
//                     y: {
//                         beginAtZero: false,
//                         title: {
//                             display: true,
//                             text: 'Weight (kg)'
//                         }
//                     },
//                     x: {
//                         title: {
//                             display: true,
//                             text: 'Date'
//                         }
//                     }
//                 },
//                 plugins: {
//                     legend: {
//                         display: true
//                     },
//                     tooltip: {
//                         mode: 'index',
//                         intersect: false
//                     }
//                 },
//                 responsive: true
//             }
//         });
//     })
//     .catch(error => console.error("❌ Chart fetch error:", error));
// }

let weightChartInstance = null;  // Keep track of the chart so we can destroy before redrawing

function updateWeightChart() {
    fetch("/api/v1/weight-data/")
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch weight data");
            return response.json();
        })
        .then(data => {
            console.log("📊 Chart Data:", data);

            const canvas = document.getElementById('weightChart');
            if (!canvas) {
                console.error("Canvas element with ID 'weightChart' not found.");
                return;
            }

            const ctx = canvas.getContext('2d');

            // Destroy previous chart if exists
            if (weightChartInstance) {
                weightChartInstance.destroy();
            }

            // Create new chart
            weightChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Weight (kg)',
                        data: data.weights, // ✅ Correct key from JSON
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.3,
                        pointBackgroundColor: 'green',
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Weight (kg)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    responsive: true
                }
            });
        })
        .catch(error => {
            console.error("❌ Chart fetch error:", error);
        });
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}

document.addEventListener("DOMContentLoaded", updateWeightChart);
// const canvas = document.getElementById('weightChart');
// if (!canvas) {
//     console.error("Canvas with id 'weightChart' not found!");
//     return 0;
// }
// const ctx = canvas.getContext('2d');
