import os
import threading
import json
import gspread
from flask import Flask
import telebot
from telebot import types
from oauth2client.service_account import ServiceAccountCredentials

# ------------------- CONFIG -------------------
BOT_TOKEN = "8449940203:AAEzE4HenalM0YuO5joqnNZIC2bLs3ACDLg"  # Tera bot token fixed
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")  # Render env var me dalna
SHEET_NAME = "Video_Submissions - Mr Profit"  # Tera sheet name fixed

# ------------------- GOOGLE SHEETS SETUP -------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads("/etc/secrets/credentials.json")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ------------------- TELEGRAM BOT -------------------
bot = telebot.TeleBot(BOT_TOKEN)

# Flask server for Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is running on Render 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

# ------------------- HANDLERS -------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    banner_url = "https://i.ibb.co/0cLzBRy/banner.jpg"  # Apna banner link dal
    bot.send_photo(message.chat.id, banner_url, caption="🎱 Paste the link of your short video")

@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    if message.text.startswith("http"):
        name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
        link = message.text

        # Save to Google Sheet
        sheet.append_row([name, username, link])

        # Success message with button
        markup = types.InlineKeyboardMarkup()
        restart_btn = types.InlineKeyboardButton("Submit Another Video", callback_data="restart")
        markup.add(restart_btn)
        bot.send_message(message.chat.id, "✅ Your video has been submitted successfully", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Please send a valid video link starting with http or https.")

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart_flow(call):
    send_welcome(call.message)

# ------------------- MAIN -------------------
if _name_ == "_main_":
    threading.Thread(target=run).start()
    bot.polling(non_stop=True)