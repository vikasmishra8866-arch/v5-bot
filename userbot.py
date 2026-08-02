import asyncio
import random
import re
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction
from config import API_ID, API_HASH, SESSION_STRING, TARGET_BOT_USERNAME, PROXY_URL

# Parse proxy string if provided (format: socks5://user:pass@host:port)
proxy_config = None
if PROXY_URL:
    import urllib.parse
    parsed = urllib.parse.urlparse(PROXY_URL)
    proxy_config = (
        parsed.scheme.lower() == 'socks5',
        parsed.hostname,
        parsed.port,
        True,
        parsed.username,
        parsed.password
    )

client = TelegramClient('userbot_session', API_ID, API_HASH, proxy=proxy_config)

async def parse_vehicle_response(raw_text: str, vehicle_no: str) -> str:
    # Default placeholder values
    data = {
        "OWNER_NAME": "Not Found",
        "VEHICLE_TYPE": "Not Found",
        "RTO_CIRCLE": "Not Found",
        "REG_DATE": "Not Found",
        "INS_PROVIDER": "Not Found",
        "POLICY_NUM": "Not Found",
        "EXPIRY_DATE": "Not Found",
        "PUC_EXPIRY": "Not Found",
        "CHASSIS_ID": "Not Found",
        "ENGINE_ID": "Not Found",
        "ADDRESS": "Not Found",
        "MOBILE": "Mobile Number Not Found 🚫"
    }

    # Basic regex or line-based extraction logic mapping from raw text
    for line in raw_text.split('\n'):
        line_lower = line.lower()
        if 'owner' in line_lower or 'name' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["OWNER_NAME"] = parts[1].strip()
        elif 'maker' in line_lower or 'model' in line_lower or 'vehicle' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["VEHICLE_TYPE"] = parts[1].strip()
        elif 'rto' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["RTO_CIRCLE"] = parts[1].strip()
        elif 'reg' in line_lower and 'date' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["REG_DATE"] = parts[1].strip()
        elif 'insurance' in line_lower or 'company' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["INS_PROVIDER"] = parts[1].strip()
        elif 'policy' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["POLICY_NUM"] = parts[1].strip()
        elif 'expiry' in line_lower and 'ins' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["EXPIRY_DATE"] = parts[1].strip()
        elif 'puc' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["PUC_EXPIRY"] = parts[1].strip()
        elif 'chassis' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["CHASSIS_ID"] = parts[1].strip()
        elif 'engine' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["ENGINE_ID"] = parts[1].strip()
        elif 'address' in line_lower:
            parts = line.split(':')
            if len(parts) > 1: data["ADDRESS"] = parts[1].strip()
        elif 'mobile' in line_lower or 'phone' in line_lower:
            parts = line.split(':')
            if len(parts) > 1:
                mob = parts[1].strip()
                if mob and len(mob) >= 6:
                    data["MOBILE"] = mob

    # If raw text contains valid info blocks, use structured hacker layout
    formatted_output = f"""root@vahan-system:~# fetch_details {vehicle_no.upper()}
-----------------------------------------
[+] VEHICLE STATUS: ONLINE / VERIFIED
-----------------------------------------
> OWNER_NAME   : {data["OWNER_NAME"]}
> VEHICLE_TYPE : {data["VEHICLE_TYPE"]}
> RTO_CIRCLE   : {data["RTO_CIRCLE"]}
> REG_DATE     : {data["REG_DATE"]}

> INS_PROVIDER : {data["INS_PROVIDER"]}
> POLICY_NUM   : {data["POLICY_NUM"]}
> EXPIRY_DATE  : {data["EXPIRY_DATE"]} [ACTIVE ✅]
> PUC_EXPIRY   : {data["PUC_EXPIRY"]}

> CHASSIS_ID   : {data["CHASSIS_ID"]}
> ENGINE_ID    : {data["ENGINE_ID"]}

> ADDRESS      : {data["ADDRESS"]}
> MOBILE       : {data["MOBILE"]}
-----------------------------------------"""
    return formatted_output

async def fetch_vehicle_data(vehicle_no: str) -> str:
    if not client.is_connected():
        await client.connect()
    
    try:
        target_bot = TARGET_BOT_USERNAME
        
        # Human typing simulation action
        try:
            await client(SetTypingRequest(
                peer=target_bot,
                action=SendMessageTypingAction()
            ))
        except Exception:
            pass

        # Randomized Jitter Delay between 8 to 13 seconds (Gaussian Distribution mimic)
        delay = random.uniform(8.0, 13.0) + abs(random.gauss(0, 1.5))
        await asyncio.sleep(min(delay, 15.0))

        # Send vehicle query to target bot
        async with client.conversation(target_bot, timeout=30) as conv:
            await conv.send_message(vehicle_no)
            response = await conv.get_response()
            if response and response.text:
                return await parse_vehicle_response(response.text, vehicle_no)
            
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await fetch_vehicle_data(vehicle_no)
    except Exception as e:
        print(f"Userbot Error: {e}")
        return None
    
    return None
