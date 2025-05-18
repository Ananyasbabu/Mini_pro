document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("addIngredientBtn").addEventListener("click", addIngredient);
    loadIngredients(); // Ensure ingredients load when the page is ready
});

// ✅ Improved CSRF Token Retrieval
function getCSRFToken() {
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfInput ? csrfInput.value : "";
}

// ✅ Corrected `input` selection
function addIngredient() {
    const input = document.getElementById("ingredientInput");  // 🔥 Fixed: Target input field
    const value = input.value.trim();

    if (!value) {
        alert("Please enter an ingredient!");
        return;
    }

    fetch("/api/v1/ingredients/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ name: value })
    })
    .then(response => {
        console.log("🔍 Raw response:", response);
        return response.json();
    })
    .then(data => {
        console.log("✅ Parsed JSON:", data);
        if (data.error) {
            console.error("🚨 API Error:", data.error);
            alert("Error: " + data.error);
        } else {
            console.log("✅ Ingredient added successfully!");
            loadIngredients(); // ✅ Reload ingredients
            input.value = "";  // ✅ Clear input field on success
        }
    })
    .catch(error => console.error("❌ Error adding ingredient:", error));
}

// ✅ Delete Ingredient
function deleteIngredient(name) {
    fetch("/api/v1/ingredients/delete/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken(),
        },
        body: "name=" + encodeURIComponent(name),
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Ingredient deleted:", data.message);
        loadIngredients(); // ✅ Refresh list
    })
    .catch(error => console.error("❌ Delete failed:", error)); // ✅ Log errors
}

// ✅ Load Ingredients
function loadIngredients() {
    fetch("/api/v1/ingredients/")
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById("ingredientList");
        list.innerHTML = ""; // ✅ Clear list before populating

        data.ingredients.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;

            const btn = document.createElement("button");
            btn.textContent = "❌";
            btn.classList.add("delete-btn");
            btn.onclick = () => deleteIngredient(item);

            li.appendChild(btn);
            list.appendChild(li);
        });
    })
    .catch(error => console.error("❌ Error loading ingredients:", error));
}

// // ✅ Get Food Suggestions
// function getFinalSuggestions() {
//     const commonFoods = {
//         banana: "🍌 Banana smoothie",
//         broccoli: "🥦 Steamed broccoli",
//         oats: "🥣 Oats bowl",
//         cucumber: "🥒 Cucumber salad",
//         quinoa: "🍚 Quinoa with stir-fried veggies",
//         apple: "🍏 Apple slices with peanut butter"
//     };

//     fetch("/get_ingredients/")
//     .then(response => response.json())
//     .then(data => {
//         let matches = data.ingredients
//             .map(ing => ing.toLowerCase())
//             .map(ing => commonFoods[ing])
//             .filter(Boolean);

//         if (matches.length === 0) {
//             matches = ["❗ Try adding more healthy ingredients!"];
//         }

//         document.getElementById("finalSuggestions").innerHTML =
//             "<strong>🥗 Suggestions Based on Ingredients:</strong> <ul>" +
//             matches.map(item => `<li>${item}</li>`).join('') + "</ul>";
//     })
//     .catch(error => console.error("❌ Error fetching suggestions:", error));
// }
