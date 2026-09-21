import os
import telebot
import yt_dlp

# Получаем токен из переменных окружения Render
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привет! Отправь мне ссылку на видео (YouTube, Shorts, TikTok и др.), и я скачаю его для тебя."
    )

@bot.message_handler(func=lambda message: message.text and message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    status_msg = bot.reply_to(message, "⏳ Скачиваю видео, подожди немного...")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024, 
        'quiet': True,
    }

    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        error_text = str(e)
        if "File is larger than the max-filesize" in error_text:
            bot.edit_message_text("❌ Ошибка: видео слишком большое (больше 50 МБ).", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Не удалось скачать видео. Проверьте ссылку.", message.chat.id, status_msg.message_id)

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

bot.infinity_polling()

