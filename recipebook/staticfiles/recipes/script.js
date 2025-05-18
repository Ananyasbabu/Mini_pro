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

    if (bmi < 18.5) category = "underweight";
    else if (bmi < 25) category = "normal";
    else if (bmi < 30) category = "overweight";
    else category = "obese";

    resultElement.innerHTML = `Your BMI is ${bmi.toFixed(2)} (${category})`;

    let foods = {
        underweight: ["Banana smoothie", "Dry fruits", "Egg sandwich"],
        normal: ["Grilled veggies", "Quinoa salad", "Fruits bowl"],
        overweight: ["Steamed broccoli", "Lentil soup", "Green tea"],
        obese: ["Cucumber salad", "Oats with fruits", "Boiled veggies"]
    };

    suggestionElement.innerHTML =
        "<strong>Suggested Foods:</strong> <ul>" +
        foods[category].map(item => `<li>${item}</li>`).join('') + "</ul>";
}
