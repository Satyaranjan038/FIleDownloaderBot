import os
import re
import urllib.parse
import requests
from io import BytesIO
from flask import Flask, request, render_template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# Initialize Flask app
app = Flask(__name__)

# Function to extract TeraBox ID
def extract_terabox_id(url):
    parsed_url = urllib.parse.urlparse(url)
    match = re.search(r"/s/([A-Za-z0-9_-]+)", parsed_url.path)
    if match:
        video_id = match.group(1)
        if video_id.startswith("1"):
            video_id = video_id[1:]
        return video_id
    return None  # No valid ID found

# Function to get the direct video link
def get_direct_video_link(url):
    video_id = extract_terabox_id(url)
    if video_id:
        return f"https://www.1024terabox.com/sharing/embed?surl={video_id}", video_id
    return None, None  # Return None if invalid URL

# Telegram Bot Commands
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hey! Send me a TeraBox link to get the streaming link.")

# Handle messages with TeraBox links
async def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text.strip()

    if "terabox.com" in message_text or "teraboxdownloader.pro" in message_text or "terasharelink.com" in message_text :
        direct_link, video_id = get_direct_video_link(message_text)

        if direct_link:
            # Generate streaming link via our Flask server
            stream_link = f"https://filedownloaderbot-jzw6.onrender.com/stream?surl={video_id}"

            # Create "🎬 Play Online" button
            keyboard = [[InlineKeyboardButton("🎬 Play Online", url=stream_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🎥 **Stream Video Online:**\n{stream_link}",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Invalid TeraBox link. Please check and try again.")
    else:
        await update.message.reply_text("❌ Please send a valid TeraBox link.")

# Flask route to serve the HTML video player
@app.route("/stream")
def stream_video():
    video_id = request.args.get("surl", "")
    if not video_id:
        return "Invalid video ID"
    
    video_url = f"https://www.1024terabox.com/sharing/embed?surl={video_id}"
    print(video_url)
    return render_template("index.html", video_url=video_url)

# Telegram bot setup
def main():
    
    TOKEN = os.getenv("BOT_TOKEN")  # Load token from environment variable
    app_telegram = Application.builder().token(TOKEN).build()

    # Handlers
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start Telegram bot in a separate thread with a proper event loop
    def run_telegram_bot():
        asyncio.set_event_loop(asyncio.new_event_loop())  # Create a new event loop
        app_telegram.run_polling()

    import threading
    threading.Thread(target=run_telegram_bot, daemon=True).start()

    # Run Flask server
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
