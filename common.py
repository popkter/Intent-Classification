
from dotenv import load_dotenv
import os

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CHAT_API_KEY = os.getenv("CHAT_API_KEY")

WEATHER_PORT = 10010
INTENT_PORT = 10000
