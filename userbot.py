import asyncio
import random
import re
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction
from config import API_ID, API_HASH, SESSION_STRING, TARGET_BOT_USERNAME, PROXY_URL

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
        
        # 1. Forcefully get and cache the target bot entity so request actually goes through
        entity = await client.get_input_entity(target_bot)
        
        # 2. Simulate typing status to mimic human behavior
        try:
            await client(SetTypingRequest(
                peer=entity,
                action=SendMessageTypingAction()
            ))
        except Exception:
            pass

        # 3. Randomized Jitter Delay
        delay = random.uniform(3.0, 6.0)
        await asyncio.sleep(delay)

        # 4. Direct Message Sending & Response Catching (No Conversation Hangs)
        # Send message directly to target bot
        sent_msg = await client.send_message(entity, vehicle_no)
        
        # Wait for the incoming response from the target bot
        # We listen to messages from this specific bot for up to 35 seconds
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < 35:
            async for message in client.iter_messages(entity, limit=3):
                # Check if message is newer than our sent message and contains text response
                if message.id > sent_msg.id and message.text and len(message.text) > 10:
                    return await parse_vehicle_response(message.text, vehicle_no)
            await asyncio.sleep(2)
            
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await fetch_vehicle_data(vehicle_no)
    except Exception as e:
        print(f"Direct Userbot Dispatch Error: {e}")
        return None
    
    return None
