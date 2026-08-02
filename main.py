import asyncio
import logging
import os
import threading
from flask import Flask, render_template, request, session
import qrcode
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import BOT_TOKEN, ADMIN_ID, UPI_ID, API_ID, API_HASH, SESSION_STRING
from database import init_db, get_or_create_user, get_user_points, deduct_point, update_points
from userbot import fetch_vehicle_data, client as userbot_client

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Flask Web Server for Render & Web Login ---
app = Flask(__name__)
app.secret_key = "super_secret_vahan_key_render_999"

@app.route('/')
def home():
    return "Vahan System Bot is Alive and Running 24/7! Go to /login to generate session string."

@app.route('/login', methods=['GET', 'POST'])
def web_login():
    step = session.get('step', 'phone')
    error = None
    session_string = None

    if request.method == 'POST':
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if step == 'phone':
            phone = request.form.get('phone').strip()
            session['phone'] = phone
            try:
                client = TelegramClient(StringSession(), API_ID, API_HASH)
                loop.run_until_complete(client.connect())
                sent = loop.run_until_complete(client.send_code_request(phone))
                session['phone_code_hash'] = sent.phone_code_hash
                session['step'] = 'code'
                step = 'code'
                client.disconnect()
            except Exception as e:
                error = str(e)
                
        elif step == 'code':
            code = request.form.get('code').strip()
            phone = session.get('phone')
            phone_code_hash = session.get('phone_code_hash')
            try:
                client = TelegramClient(StringSession(), API_ID, API_HASH)
                loop.run_until_complete(client.connect())
                try:
                    loop.run_until_complete(client.sign_in(phone, code, phone_code_hash=phone_code_hash))
                    session_string = client.session.save()
                    session['step'] = 'success'
                    step = 'success'
                except Exception as ex:
                    if '2FA' in str(ex) or 'password' in str(ex).lower():
                        session['step'] = 'password'
                        step = 'password'
                    else:
                        raise ex
                client.disconnect()
            except Exception as e:
                error = str(e)
                
        elif step == 'password':
            password = request.form.get('password').strip()
            try:
                client = TelegramClient(StringSession(), API_ID, API_HASH)
                loop.run_until_complete(client.connect())
                loop.run_until_complete(client.sign_in(password=password))
                session_string = client.session.save()
                session['step'] = 'success'
                step = 'success'
                client.disconnect()
            except Exception as e:
                error = str(e)

    return render_template('login.html', step=step, error=error, session_string=session_string)

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
# ---------------------------------------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    points = await get_or_create_user(user_id, username, first_name)
    
    if user_id == int(ADMIN_ID):
        welcome_text = (
            f"👑 **ADMIN PANEL / SECURE VAHAN SYSTEM** 👑\n\n"
            f"Welcome, Admin `{first_name}`!\n"
            f"✨ **Status:** Unlimited Free Searches Allowed 🟢\n\n"
            f"Send any vehicle number (e.g., `GJ05CX0863`) to fetch live details instantly."
        )
    else:
        welcome_text = (
            f"🔐 **SECURE VAHAN QUERY SYSTEM** 🔐\n\n"
            f"Welcome, `{first_name}`!\n"
            f"Your Current Balance: **{points} Free Points**\n\n"
            f"Send any vehicle number (e.g., `GJ05CX0863`) to fetch live details instantly."
        )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_vehicle_search(message: types.Message):
    user_id = message.from_user.id
    vehicle_no = message.text.strip()
    
    is_admin = (user_id == int(ADMIN_ID))
    
    if not is_admin:
        points = await get_user_points(user_id)
        if points <= 0:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💎 Get Points / Recharge", callback_data="recharge_menu")]
            ])
            await message.answer("❌ **Access Denied:** Your balance is 0 points. Please recharge to continue searching.", reply_markup=keyboard, parse_mode="Markdown")
            return
        await deduct_point(user_id)

    processing_msg = await message.answer("🔄 `Connecting to target bot & fetching details...`", parse_mode="Markdown")
    
    result_text = await fetch_vehicle_data(vehicle_no)
    
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
    except Exception:
        pass
    
    if not result_text:
        await message.answer("⚠️ Target service is currently unreachable or busy. Your point has been refunded.")
        if not is_admin:
            await update_points(user_id, 1)
        return

    warning_footer = "\n\n*⚠️ This data will be automatically deleted in 20 minutes for security and privacy.*"
    sent_result = await message.answer(f"```text\n{result_text}\n
