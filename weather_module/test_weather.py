
from weather_api import get_weather_data
from weather_risk import calculate_disease_risk


location_name = input("Enter village or district: ")

try:
    result = get_weather_data(location_name)

    if result is None:
        print("Location not found.")
    else:
        location = result["location"]
        weather = result["weather"]

        print("\nLocation:", location["name"])
        print("State:", location.get("admin1", "N/A"))

        current = weather["current"]

        print("\nCurrent Weather")
        print("Temperature:", current["temperature_2m"], "°C")
        print("Humidity:", current["relative_humidity_2m"], "%")
        print("Precipitation:", current["precipitation"], "mm")

        print("\n7-Day Forecast")

        for i, date in enumerate(weather["daily"]["time"]):
            print(
                date,
                "Max:", weather["daily"]["temperature_2m_max"][i],
                "Min:", weather["daily"]["temperature_2m_min"][i],
                "Rain:", weather["daily"]["precipitation_sum"][i]
            )

        print("\nDisease Risk")
        risks = calculate_disease_risk(weather)

        for disease, details in risks.items():
            print(disease, ":", details["risk"])

except Exception as e:
    print("Error:", e)
