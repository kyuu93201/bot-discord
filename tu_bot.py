import discord
import os
from discord.ext import commands
from flask import Flask
import threading

# ----------------------------
# Web server nhỏ để giữ bot online
# ----------------------------
app = Flask('')

@app.route('/')
def home():
    return "Tú bot đang hoạt động!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

# ----------------------------
# Discord bot
# ----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} đã sẵn sàng!")

# ----------------------------
# Khi có tin nhắn
# ----------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Nếu ai đó mention @tú
    if bot.user.mentioned_in(message):
        await message.channel.send("im nào cô bé")

        # Gửi ảnh (đảm bảo file gay.png có trong thư mục bot)
        await message.channel.send(
            file=discord.File("gay.png")
        )

    await bot.process_commands(message)

# ----------------------------
# Lệnh test
# ----------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# ----------------------------
# Chạy bot
# ----------------------------
token = os.getenv("DISCORD_TOKEN")
if not token:
    print("❌ Thiếu biến môi trường DISCORD_TOKEN")
else:
    bot.run(token)
