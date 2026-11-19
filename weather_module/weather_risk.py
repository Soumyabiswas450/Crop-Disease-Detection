
def calculate_disease_risk(weather_data):
    """
    Preliminary weather-based screening.
    This is not a validated disease forecasting model.
    """

    current = weather_data["current"]
    daily = weather_data["daily"]

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")

    if temperature is None or humidity is None:
        blast = {
            "risk": "Not assessed",
            "score": None,
            "reason": "Required weather data is unavailable."
        }

    else:
        score = 0
        reasons = []

        # Temperature screening indicator
        if 17 <= temperature <= 28:
            score += 1
            reasons.append("Temperature is within a favourable range.")

        # Humidity screening indicator
        if humidity >= 90:
            score += 1
            reasons.append("Very high relative humidity.")

        # Check forecast rainfall
        rainfall = daily.get("precipitation_sum", [])

        if rainfall and max(rainfall) >= 10:
            score += 1
            reasons.append("Significant rainfall is forecast.")

        if score >= 3:
            risk = "High weather favourability"
        elif score == 2:
            risk = "Moderate weather favourability"
        elif score == 1:
            risk = "Some favourable conditions"
        else:
            risk = "Low weather favourability"

        blast = {
            "risk": risk,
            "score": score,
            "reason": " ".join(reasons) if reasons
                      else "No selected favourable indicators detected."
        }

    return {
        "Rice Blast": blast,

        "Brown Spot": {
            "risk": "Not assessed",
            "score": None,
            "reason": "A validated disease-specific weather model is needed."
        },

        "False Smut": {
            "risk": "Not assessed",
            "score": None,
            "reason": "Crop growth stage, especially booting and flowering, is required."
        },

        "Tungro": {
            "risk": "Not assessed",
            "score": None,
            "reason": "Green leafhopper and virus monitoring are required."
        }
    }
