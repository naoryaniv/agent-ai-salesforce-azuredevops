from dotenv import load_dotenv
import os

load_dotenv()

SSL_CERT_FILE = os.environ.get("SSL_CERT_FILE")

ORGANIZATION = os.getenv("ORGANIZATION")
PERSONAL_ACCESS_TOKEN = os.getenv("PERSONAL_ACCESS_TOKEN")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_PROXY_URL = os.environ.get("OPENAI_PROXY_URL", "")

MODEL = os.getenv("MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))


