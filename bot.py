import os
import json
import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== Environment Variables =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway pe env var me set karna hoga
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")  # poora JSON string
SHEET_NAME = os.getenv("SHEET_NAME", "Video_Submissions")  # default name

# Bot setup
bot = telebot.TeleBot(BOT_TOKEN)

# ===== Google Sheets Auth =====
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open(SHEET_NAME).sheet1

# ===== Banner Path =====
BANNER_PATH = "banner.jpg"  # Banner file ko project folder me rakho

# ===== Start Command =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        with open(BANNER_PATH, 'rb') as banner:
            bot.send_photo(message.chat.id, banner)
    except:
        bot.send_message(message.chat.id, "🎱 Paste the link of your short video")
    else:
        bot.send_message(message.chat.id, "🎱 Paste the link of your short video")
    
    bot.register_next_step_handler(message, process_video_link)

# ===== Process Video Link =====
def process_video_link(message):
    video_link = message.text
    username = message.from_user.username if message.from_user.username else "No Username"
    full_name = message.from_user.first_name
    sheet.append_row([full_name, username, video_link])

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Submit another video", callback_data="submit_another"))
    bot.send_message(message.chat.id, "✅ Your video has been submitted successfully", reply_markup=markup)

# ===== Handle Button Click =====
@bot.callback_query_handler(func=lambda call: call.data == "submit_another")
def handle_submit_another(call):
    send_welcome(call.message)

print("Bot is running on Railway...")
bot.polling()
