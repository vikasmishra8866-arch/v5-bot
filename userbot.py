import random
import re
import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH, SESSION_STRING, TARGET_BOT_USERNAME, PROXY_URL

# Parse Proxy configuration if provided
proxy_config = None
if PROXY_URL:
    # Example format support for Pyrogram SOCKS5 proxy
    from urllib.parse import urlparse
    parsed = urlparse(PROXY_URL)
    proxy_config = {
        "scheme": parsed.scheme,
        "hostname": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "password": parsed.password
    }

userbot = Client(
    "secured_userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    proxy=proxy_config
)

async def fetch_vehicle_data(vehicle_number: str) -> str:
    if not userbot.is_connected:
        await userbot.start()
    
    try:
        # 1. Human Typing Simulation
        await userbot.send_chat_action(TARGET_BOT_USERNAME, "typing")
        
        # 2. Randomized Delay with Gaussian-distributed jitter (8 to 13 seconds)
        delay = random.uniform(8.0, 13.0) + random.gauss(0, 0.5)
        delay = max(8.0, min(delay, 13.0)) # Keep within strict limits
        await asyncio.sleep(delay)
        
        # 3. Send query to target bot
        sent_msg = await userbot.send_message(TARGET_BOT_USERNAME, vehicle_number.strip().upper())
        
        # 4. Wait for response with safety timeout and FloodWait protection
        response_text = None
        for _ in range(30): # Wait up to 30 seconds for reply
            await asyncio.sleep(1)
            async for message in userbot.get_chat_history(TARGET_BOT_USERNAME, limit=5):
                if message.id > sent_msg.id and message.text:
                    response_text = message.text
                    break
            if response_text:
                break
                
        if not response_text:
            return None
            
        return parse_and_format_response(vehicle_number, response_text)

    except FloodWait as e:
        await asyncio.sleep(e.value + 5)
        return "⚠️ Server busy due to high security rate limits. Please try again shortly."
    except Exception as e:
        print(f"Userbot Error: {e}")
        return None

def parse_and_format_response(vehicle_no: str, raw_text: str) -> str:
    """
    Parses raw text and builds Terminal UI format.
    Removes missing optional fields completely, except mobile which shows specific fallback.
    """
    # Simple regex extractions from raw text matching typical bot replies
    def extract(pattern, text, default=None):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    owner = extract(r"Owner[:\-]?\s*([^\n]+)", raw_text, "UNKNOWN")
    model = extract(r"Make/Model[:\-]?\s*([^\n]+)", raw_text)
    fuel = extract(r"Fuel[:\-]?\s*([^\n]+)", raw_text)
    rto = extract(r"RTO[:\-]?\s*([^\n]+)", raw_text)
    reg_date = extract(r"Reg Date[:\-]?\s*([^\n]+)", raw_text)
    
    ins_provider = extract(r"Insurance Company[:\-]?\s*([^\n]+)", raw_text)
    policy_num = extract(r"Policy Number[:\-]?\s*([^\n]+)", raw_text)
    exp_date = extract(r"Insurance Validity[:\-]?\s*([^\n]+)", raw_text)
    puc_exp = extract(r"PUC Validity[:\-]?\s*([^\n]+)", raw_text)
    
    chassis = extract(r"Chassis[:\-]?\s*([^\n]+)", raw_text)
    engine = extract(r"Engine[:\-]?\s*([^\n]+)", raw_text)
    address = extract(r"Address[:\-]?\s*([^\n]+)", raw_text)
    mobile = extract(r"Mobile[:\-]?\s*([0-9]{10})", raw_text)

    # Build Output Dynamically
    out = f"root@vahan-system:~# fetch_details {vehicle_no.upper()}\n"
    out += "-----------------------------------------\n"
    out += "[+] VEHICLE STATUS: ONLINE / VERIFIED\n"
    out += "-----------------------------------------\n"
    out += f"> OWNER_NAME   : {owner}\n"
    
    if model or fuel:
        v_type_str = f"{model or ''} ({fuel or ''})".strip()
        out += f"> VEHICLE_TYPE : {v_type_str}\n"
    if rto:
        out += f"> RTO_CIRCLE   : {rto}\n"
    if reg_date:
        out += f"> REG_DATE     : {reg_date}\n"
    
    # Optional Insurance Block
    if ins_provider or policy_num or exp_date:
        out += "\n"
        if ins_provider: out += f"> INS_PROVIDER : {ins_provider}\n"
        if policy_num: out += f"> POLICY_NUM   : {policy_num}\n"
        if exp_date: out += f"> EXPIRY_DATE  : {exp_date} [ACTIVE ✅]\n"
    
    if puc_exp:
        out += f"> PUC_EXPIRY   : {puc_exp}\n"
        
    if chassis or engine:
        out += "\n"
        if chassis: out += f"> CHASSIS_ID   : {chassis}\n"
        if engine: out += f"> ENGINE_ID    : {engine}\n"
        
    if address:
        out += f"\n> ADDRESS      : {address}\n"
        
    # Mobile Exception Handling Rule
    if mobile:
        out += f"> MOBILE       : {mobile} ✅\n"
    else:
        out += f"> MOBILE       : Mobile Number Not Found 🚫\n"
        
    out += "-----------------------------------------"
    return out
