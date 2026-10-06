# Basic Weather App

A Tkinter desktop weather dashboard for a city or postal code. It shows current temperature, feels-like temperature, humidity, wind, condition symbol, the next six hourly forecasts, and a five-day forecast. The C/F button switches temperature units without another network request.

## Run

From PowerShell:

```powershell
cd "C:\Users\Sreeyakeshrajan_T\OneDrive\Desktop\OIBSIP\PYTHON PROGRAMMING\Weather App"
python -m pip install -r requirements.txt
python weather_app.py
```

Enter a city such as `London`, a city and country such as `Paris, France`, or a ZIP/postal code recognized by the geocoding service. Press Enter or select **Get Weather**. **Use My Location** requests an approximate location from IP metadata and then fetches the forecast for that city.

## Data source and error handling

Weather/geocoding are provided by [Open-Meteo](https://open-meteo.com/), an API alternative that does not require an API key. Location search uses the [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api); conditions and forecasts use the [Forecast API](https://open-meteo.com/en/docs). The automatic location button uses [ipinfo.io](https://ipinfo.io/) without an access token; this is approximate IP-based location, not GPS.

Requests run off the GUI thread so the window remains responsive. Empty input, no matching location, rate limiting, timeouts, connection errors, and API errors are shown in the window. Weather icons use Unicode symbols based on Open-Meteo weather codes.

## Privacy

- The city or postal code entered is sent to Open-Meteo's geocoder; coordinates returned by that service are sent to its forecast endpoint.
- Approximate IP location is **only** requested when you press **Use My Location**. Your network IP is necessarily visible to the IP lookup service. The returned city is used for the weather lookup.
- The app does not request browser geolocation, save location history, or persist API responses.

## Tests

Run the offline tests (API calls are mocked):

```powershell
python -m unittest discover -s tests -v
```
