from flask import Flask, render_template, request
from waitress import serve
import requests
import geocoder
import os

app = Flask(__name__)

API_KEY = "0001011a7c9772a5ca2c46428326d81b"

LANG = "en"

TEXT = {
    "en": {
        "title": "Weather",
        "search": "Search City",
        "gps": "Use GPS 🌍",
        "empty": "Enter a city",
        "notfound": "City not found",
        "net": "Network error",
        "error": "Error"
    },
    "cz": {
        "title": "Počasí",
        "search": "Hledat město",
        "gps": "Použít GPS 🌍",
        "empty": "Zadej město",
        "notfound": "Město nenalezeno",
        "net": "Chyba sítě",
        "error": "Chyba"
    }
}


def get_location():
    try:
        g = geocoder.ip("me")
        return g.latlng, g.city
    except:
        return None, None


def get_weather(lat, lon, city_name, lang):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang={lang}"

    try:
        data = requests.get(url).json()
    except:
        return TEXT[lang]["net"]

    if str(data.get("cod")) != "200":
        return TEXT[lang]["notfound"]

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    weather = data["weather"][0]["description"]

    icon = ""
    if "clear" in weather:
        icon = "☀️"
    elif "cloud" in weather:
        icon = "☁️"
    elif "rain" in weather:
        icon = "🌧️"
    elif "snow" in weather:
        icon = "❄️"

    return f"""
{icon} {weather.capitalize()}

📍 {city_name}
🌡️ Temp: {temp}°C
🤔 Feels: {feels}°C
💧 Humidity: {humidity}%
💨 Wind: {wind} m/s
"""


@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    lang = request.form.get("lang", "en")

    if request.method == "POST":

        if "city" in request.form:
            city = request.form["city"].strip()

            if not city:
                result = TEXT[lang]["empty"]
            else:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
                data = requests.get(geo_url).json()

                if not data:
                    result = TEXT[lang]["notfound"]
                else:
                    lat = data[0]["lat"]
                    lon = data[0]["lon"]
                    result = get_weather(lat, lon, city, lang)

        elif "gps" in request.form:
            loc, city = get_location()

            if not loc:
                result = TEXT[lang]["error"]
            else:
                lat, lon = loc
                result = get_weather(lat, lon, city or "My Location", lang)

    return render_template("index.html", result=result, lang=lang, text=TEXT[lang])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    serve(app, host="0.0.0.0", port=port)
