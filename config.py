import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8846767321:AAE_oAlKXmnKmXOw3of1UdVsFKFJTcCL25E")
API_ID = int(os.getenv("API_ID", "36281716"))
API_HASH = os.getenv("API_HASH", "48ceca855a9c556cb52f4872b1db60ca")

SESSION_STRING = os.getenv(
    "SESSION_STRING", "1BVtsOJkBu4TWAzSYDFKp08nA79oCc_x1TlGKYzvKygFvsfiv0p99NvlC0OCV3clidNrNFRwqsZG1pgXAFPeSAjB2f6ZNAh0NwQYBkU2--RsgHL6NrSQ5U8rCKC0rixWnQgPc9pjShr4bbRC55TS1LUUShmOBbhn5igC8XSUMqANJp9brZ9DuvduRP1cUYIiHGQ5hb4_sUSP7H_dt29X5yYWYKK2IcNWapbHMkAMPa8n-dYxLjYwVrlrNMVamhHF5E81NtTngIxVxZzBmGDhai1aFfwifbyKxdW4LUjam-I2oo_noGX33e-T3e6ackRMiTt0mjO8Ir1_oLHHvJk1_cOnp-hg7J7s="
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "8204069256")) # Yahan apni Telegram ID daal dein
TARGET_BOT_USERNAME = os.getenv("TARGET_BOT_USERNAME", "@V5rtobot") # Purane bot ka username
UPI_ID = os.getenv("UPI_ID", "9696159863.wallet@phonepe")
PROXY_URL = os.getenv("PROXY_URL", None)
