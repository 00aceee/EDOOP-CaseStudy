from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

print("GMAIL_ADDRESS:", os.getenv("GMAIL_ADDRESS"))
print("GMAIL_APP:", os.getenv("GMAIL_APP"))
