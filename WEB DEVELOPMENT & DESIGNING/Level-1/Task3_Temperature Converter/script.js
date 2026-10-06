const temperatureInput =
    document.getElementById("temperature");

const unitSelect =
    document.getElementById("unit");

const convertButton =
    document.getElementById("convertBtn");

const errorMessage =
    document.getElementById("errorMessage");

const celsiusResult =
    document.getElementById("celsiusResult");

const fahrenheitResult =
    document.getElementById("fahrenheitResult");

const kelvinResult =
    document.getElementById("kelvinResult");


// Convert temperature

convertButton.addEventListener("click", function () {

    const inputValue =
        temperatureInput.value.trim();

    const unit =
        unitSelect.value;


    // Empty input

    if (inputValue === "") {

        showError(
            "Please enter a temperature value."
        );

        clearResults();

        return;
    }


    // Numeric validation

    const temperature =
        Number(inputValue);

    if (!Number.isFinite(temperature)) {

        showError(
            "Please enter a valid numeric temperature."
        );

        clearResults();

        return;
    }


    let celsius;
    let fahrenheit;
    let kelvin;


    // Celsius

    if (unit === "celsius") {

        celsius = temperature;

        fahrenheit =
            (temperature * 9 / 5) + 32;

        kelvin =
            temperature + 273.15;
    }


    // Fahrenheit

    else if (unit === "fahrenheit") {

        fahrenheit = temperature;

        celsius =
            (temperature - 32) * 5 / 9;

        kelvin =
            celsius + 273.15;
    }


    // Kelvin

    else if (unit === "kelvin") {

        kelvin = temperature;

        celsius =
            temperature - 273.15;

        fahrenheit =
            (celsius * 9 / 5) + 32;
    }


    // Absolute zero validation

    if (celsius < -273.15) {

        showError(
            "Temperature cannot be below absolute zero (-273.15°C)."
        );

        clearResults();

        return;
    }


    hideError();


    // Display results

    celsiusResult.textContent =
        celsius.toFixed(2) + " °C";

    fahrenheitResult.textContent =
        fahrenheit.toFixed(2) + " °F";

    kelvinResult.textContent =
        kelvin.toFixed(2) + " K";

});


// Show error

function showError(message) {

    errorMessage.textContent = message;

    errorMessage.style.display = "block";
}


// Hide error

function hideError() {

    errorMessage.textContent = "";

    errorMessage.style.display = "none";
}


// Clear results

function clearResults() {

    celsiusResult.textContent = "--";

    fahrenheitResult.textContent = "--";

    kelvinResult.textContent = "--";
}