from requests import get as requests_get

from src.utils import Singleton


WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather?lang=ru&units=metric&q={q}&APPID={appid}'


class WeatherAPI(Singleton):
    def __init__(self, token: str) -> None:
        self.token = token

    def get_city_weather(self, city_name: str) -> dict:
        response = requests_get(
            WEATHER_API_URL.format(q=city_name, appid=self.token)
        )

        data = response.json()
        if response.status_code == 200:
            return {
                'success': True,
                'temp': data['main']['temp'],
                'desc': data['weather'][0]['description'],
                'city': data['name']
            }
        else:
            print(data)
        return {'success': False}
