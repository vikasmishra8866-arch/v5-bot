import asyncio
import logging
import os
import qrcode
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from config import BOT_TOKEN, ADMIN_ID, UPI_ID
from database import init_db, get_or_create_user, get_user_points, deduct_point, update_points
from userbot import fetch_vehicle_data

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    points = await get_or_create_user(user_id, username, first_name)
    
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
    
    points = await get_user_points(user_id)
    if points <= 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Get Points / Recharge", callback_data="recharge_menu")]
        ])
        await message.answer("❌ **Access Denied:** Your balance is 0 points. Please recharge to continue searching.", reply_markup=keyboard, parse_mode="Markdown")
        return

    # Deduct point & notify
    await deduct_point(user_id)
    processing_msg = await message.answer("🔄 `Connecting to secure database & fetching details...`", parse_mode="Markdown")
    
    # Fetch from target bot via secured Userbot
    result_text = await fetch_vehicle_data(vehicle_no)
    await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
    
    if not result_text:
        await message.answer("⚠️ Target service is currently unreachable or busy. Your point has been refunded.")
        await update_points(user_id, 1) # Refund
        return

    warning_footer = "\n\n*⚠️ This data will be automatically deleted in 20 minutes for security and privacy.*"
    sent_result = await message.answer(f"```text\n{result_text}\n```" + warning_footer, parse_mode="Markdown")
    
    # 20 Minutes Auto-Deletion Timer
    asyncio.create_task(auto_delete_message(message.chat.id, sent_result.message_id, 1200))

async def auto_delete_message(chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

@dp.callback_query(F.data == "recharge_menu")
async def recharge_menu(callback: types.CallbackQuery):
    plans_text = (
        "💎 **SELECT RECHARGE PLAN**\n\n"
        "• **15 INR** = 1 Point\n"
        "• **60 INR** = 6 Points\n"
        "• **120 INR** = 15 Points + 3 Bonus = **18 Points**\n\n"
        "Select a plan below to generate secure payment QR:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 Point (₹15)", callback_data="plan_1")],
        [InlineKeyboardButton(text="6 Points (₹60)", callback_data="plan_6")],
        [InlineKeyboardButton(text="18 Points (₹120)", callback_data="plan_18")]
    ])
    await callback.message.edit_text(plans_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("plan_"))
async def select_plan(callback: types.CallbackQuery):
    plan_qty = callback.data.split("_")[1]
    prices = {"1": "15", "6": "60", "18": "120"}
    amount = prices.get(plan_qty, "15")
    
    # Generate UPI QR Code
    upi_url = f"upi://pay?pa={UPI_ID}&pn=VahanAdmin&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    path = f"qr_{callback.from_user.id}.png"
    img.save(path)
    
    caption = (
        f"📱 **SCAN & PAY (UPI)**\n\n"
        f"Amount: **₹{amount}** for **{plan_qty} Points**\n"
        f"UPI ID: `{UPI_ID}`\n\n"
        f"📸 After payment, send screenshot & your User ID to Admin.\n"
        f"*⚠️ This QR code will automatically self-destruct in 5 minutes.*"
    )
    
    photo = BufferedInputFile(open(path, "rb").read(), filename="qr.png")
    qr_msg = await callback.message.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")
    if os.path.exists(path):
        os.remove(path)
        
    # Notify Admin instantly with Action Buttons
    user = callback.from_user
    admin_notif = (
        f"🔔 **NEW PAYMENT REQUEST**\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🔖 Username: @{user.username if user.username else 'None'}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"📦 Selected Plan: {plan_qty} Points (₹{amount})"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"Give {plan_qty} Pts", callback_data=f"give_{user.id}_{plan_qty}"),
            InlineKeyboardButton(text="Reject", callback_data=f"reject_{user.id}")
        ]
    ])
    await bot.send_message(ADMIN_ID, admin_notif, reply_markup=admin_kb, parse_mode="Markdown")
    
    # 5 Minutes QR Auto-Deletion
    asyncio.create_task(auto_delete_message(callback.message.chat.id, qr_msg.message_id, 300))
    await callback.answer()

@dp.callback_query(F.data.startswith("give_"))
async def admin_give_points(callback: types.CallbackQuery):
    _, target_user_id, pts = callback.data.split("_")
    target_user_id = int(target_user_id)
    pts = int(pts)
    
    await update_points(target_user_id, pts)
    await callback.message.edit_text(callback.message.text + f"\n\n✅ **Approved & Credited {pts} Points!**")
    
    try:
        await bot.send_message(target_user_id, f"🎉 Your payment has been verified by Admin! **{pts} Points** have been added to your balance.")
    except Exception:
        pass
    await callback.answer("Points credited successfully!")

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: types.CallbackQuery):
    target_user_id = int(callback.data.split("_")[1])
    await callback.message.edit_text(callback.message.text + "\n\n❌ **Payment Rejected.**")
    try:
        await bot.send_message(target_user_id, "❌ Your payment verification was rejected by Admin. Contact support for help.")
    except Exception:
        pass
    await callback.answer("Request rejected.")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
