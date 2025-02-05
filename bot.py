import re
import os
import urllib.parse
import requests
from io import BytesIO
from flask import Flask, request, render_template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Initialize Flask app
app = Flask(__name__)

# Function to extract the correct TeraBox ID
def extract_terabox_id(url):
    parsed_url = urllib.parse.urlparse(url)
    match = re.search(r"/s/([A-Za-z0-9_-]+)", parsed_url.path)
    if match:
        video_id = match.group(1)
        if video_id.startswith("1"):  # Remove extra "1" if present
            video_id = video_id[1:]
        return video_id
    return None  # No valid ID found

# Function to get the direct video link
def get_direct_video_link(url):
    video_id = extract_terabox_id(url)
    if video_id:
        return f"https://www.1024terabox.com/sharing/embed?surl={video_id}", video_id
    return None, None  # Return None if invalid URL

# Function to get the video thumbnail
def get_video_thumbnail(video_id):
    return f"https://www.1024terabox.com/sharing/preview/surl/{video_id}.jpg"

# Function to download the image
def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)  # Convert image to bytes
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None  # Return None if failed

# Flask route to serve the HTML streaming page
@app.route("/")
def home():
    return "Terabox Telegram Bot is Running!"

@app.route("/stream")
def stream_video():
    """Renders the streaming page with the correct video link."""
    video_id = request.args.get("surl", "")
    if not video_id:
        return "Invalid video ID"
    
    video_url = f"https://www.1024terabox.com/sharing/embed?surl={video_id}"
    return render_template("index.html", video_url=video_url)

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hey! I am alive. Send me a TeraBox link to get the direct video link.")

# Message handler for extracting and sending video links
async def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text.strip()

    if "terabox.com" in message_text or "teraboxdownloader.pro" in message_text or "terasharelink.com" in message_text:
        direct_link, video_id = get_direct_video_link(message_text)

        if direct_link:
            thumbnail_url = get_video_thumbnail(video_id)
            image = download_image(thumbnail_url)  # Try downloading the image

            # Streaming link via our hosted Flask page
            stream_link = f"https://your-render-url.onrender.com/stream?surl={video_id}"

            # Create "🎬 Online Play" button
            keyboard = [[InlineKeyboardButton("🎬 Play Online", url=stream_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if image:
                # If image is available, send it with the video link
                await update.message.reply_photo(
                    photo=image,
                    caption=f"🎥 **Stream Video Online:**\n{stream_link}",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                # If image fails, still send the video link with the "🎬 Online Play" button
                await update.message.reply_text(
                    f"🎥 **Stream Video Online:**\n{stream_link}",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text("❌ Invalid TeraBox link. Please check and try again.")
    else:
        await update.message.reply_text("❌ Please send a valid TeraBox link.")

# Main function to run the bot
def main():
    TOKEN = os.getenv("BOT_TOKEN")  # Replace with your Telegram Bot token
    app_telegram = Application.builder().token(TOKEN).build()

    # Handlers
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start Telegram bot in a separate thread
    import threading
    threading.Thread(target=app_telegram.run_polling, daemon=True).start()

    # Run Flask server
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
