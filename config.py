import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8846767321:AAFIg82UDaL8H_ZGwDK6AQS3-l9zLWuNr6U")
API_ID = int(os.getenv("API_ID", "36281716"))
API_HASH = os.getenv("API_HASH", "48ceca855a9c556cb52f4872b1db60ca")

SESSION_STRING = os.getenv(
    "SESSION_STRING", 
    "1BVtsOJkBuxIYz0VK6WX-SJiNBuIdOwG6eOqROe0wwaJLC1LocoK1H_7rWnlf2RJdjwtixsF6uqcql5X1pXg3EugWj9x4N9pd-OZsyBWaebJ-iekflPXPAzjDsb2ilODPyG0joD6aDsPcuLFiIx9ytsCOy2VZbN4gmBTEq-O4i_MNnX6M7t4a9UU-0Q-q7V4acJzr3R3qGGuFPqO9DOcg5NIUHxfuTFuhYzAeB1RqrJn_FtnrYRCsN-V2AjDJv7LKI14fOQp1mxgXeZ2fU6y-lOCj--4jjtWk46Ty3_52V-VuObIf0FL6mvn8sZkP2TcwIU2raL3lXnPmB7i4-ATaLIsFsy6JWzc="
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "8204069256"))
TARGET_BOT_USERNAME = os.getenv("TARGET_BOT_USERNAME", "@V5rtobot")
UPI_ID = os.getenv("UPI_ID", "9696159863.wallet@phonepe")
PROXY_URL = os.getenv("PROXY_URL", None)
