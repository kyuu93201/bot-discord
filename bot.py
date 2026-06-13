import sys
import subprocess
import random

try:
    import discord
except ImportError:
    print("[.] Khong tim thay discord.py. Dang tu dong cai dat...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py"])
    import discord

from discord.ext import commands  

# CẤU HÌNH KHỞI TẠO INTENTS CHUẨN ĐỂ ĐỌC ĐƯỢC THÀNH VIÊN
intents = discord.Intents.default()
intents.message_content = True  # Quyền đọc tin nhắn chat
intents.members = True          # BẬT THÊM DÒNG NÀY: Quyền đọc danh sách thành viên trong Server

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# TẮT LỆNH HELP MẶC ĐỊNH ĐỂ TỰ THIẾT KẾ MENU RIÊNG
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==========================================
# DATA & CẤU HÌNH HỆ THỐNG
# ==========================================
msg_list = [
    {"text": "Ủa cái phòng này có ai gánh không, hay để tôi lùi bước về sau?", "emoji": "<:meme:1484203691576655952>"},
    {"text": "Nhìn sảnh chờ uy tín thế này chắc tí nữa bay màu trong 1 nốt nhạc!", "emoji": "<:download2:1484203699101368562>"},
    {"text": "Game này dễ, để tôi làm vài đường cơ bản là gánh tạ cho cả lũ ngay!", "emoji": "<:aihi_:1484203693661225001>"},
    {"text": "Sẵn sàng hết chưa? Bấm nút Ready đi chứ đợi chờ gì tầm này nữa!", "emoji": "<:nE:1484203703811702967>"},
    {"text": "Anh em đâu rồi? Vào chấm một chấm, lấp đầy slot sảnh chờ đi nào!", "emoji": "<:download1:1484203696123543723>"},
    {"text": "Vừa bay thẳng vào sảnh chờ xong, tính làm tí game làm quen tí nhỉ?", "emoji": "<:download:1484203701282537632>"}
]

game_list = ["Minecraft", "Valorant", "League of Legends", "Arena Breakout", "PUBG", "Genshin Impact"]

lobby_players = []       
player_points = {}       
has_claimed_daily = set() 

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"[+] BOT TU TRONG TAI VIP PRO DA ONLINE!")
    print(f"[+] Go '!cuu' trong Discord de xem menu huong dan.")
    print(f"==================================================")

# ==========================================
# TÍNH NĂNG MỚI: MENU HƯỚNG DẪN !help CỰC ĐẸP
# ==========================================
@bot.command(name="cuu")
async def help_command(ctx):
    # Khởi tạo một khung Embed màu xanh dương đậm (0x3498db)
    embed = discord.Embed(
        title="🤖 MENU HƯỚNG DẪN - BOT TÚ TRỌNG TÀI v2.0",
        description="Chào anh em! Dưới đây là toàn bộ danh sách câu lệnh và công dụng thần thánh của tôi trong Server này.",
        color=0x3498db
    )
    
    # Thêm ảnh thumbnail hoặc avatar của bot nếu muốn (ở đây để trống hoặc dùng avatar bot)
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
        
    # Thêm các danh mục lệnh phân chia scannable, rõ ràng
    embed.add_field(
        name="🎮 Quản Lý Sảnh Chờ & Thơ Ca",
        value="`!random` : Thả trạng thái sảnh chờ ngẫu nhiên kèm Big Emoji siu cuốn.\n"
              "`!slot` : Đặt gạch đăng ký 1 chân vào sảnh chờ (Tối đa 5 slot, đủ mạng tự tag réo).\n"
              "`!out` : Hủy đặt gạch, rút lui khỏi sảnh chờ nếu có việc bận.",
        inline=False
    )
    
    embed.add_field(
        name="🎲 Giải Trí & Nhân Phẩm Game Thủ",
        value="`!ganh` : Bốc ngẫu nhiên 1 ông trong server để xem quẻ tỉ lệ gánh team hay bóp team hôm nay.\n"
              "`!game` : Vòng quay may mắn biểu quyết hộ xem cả lũ nên chơi trò gì, cấm cãi lệnh chủ phòng.",
        inline=False
    )
    
    embed.add_field(
        name="💰 Sòng Bạc Xu Sảnh Chờ (Tiền Ảo)",
        value="`!daily` : Điểm danh nhận trợ cấp từ 100 đến 500 Xu miễn phí mỗi ngày.\n"
              "`!dice <số_xu>` : Đặt cược xu chơi đổ xúc xắc đỏ đen với Bot Tú. Thắng x2 xu, thua ra đê!",
        inline=False
    )
    
    # Dòng chân trang trang trí
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author.display_name} • Giữ sảnh chờ luôn rực lửa!", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    # Bot gửi khung Embed xịn sò này vào kênh chat
    await ctx.send(embed=embed)
    print(f"[Bot] Da gui menu !help cho user {ctx.author}")


# ==========================================
# CÁC LỆNH TÍNH NĂNG CŨ (GIỮ NGUYÊN LOGIC)
# ==========================================
@bot.command(name="random")
async def random_command(ctx):
    chosen = random.choice(msg_list)
    await ctx.send(f"📢 {chosen['text']}")
    await ctx.send(chosen['emoji'])

@bot.command(name="slot")
async def slot_command(ctx):
    global lobby_players
    player = ctx.author
    if player in lobby_players:
        await ctx.send(f"❌ {player.mention} ơi, ông đã đặt gạch trong sảnh từ trước rồi nha!")
        return
    if len(lobby_players) >= 5:
        await ctx.send(f"❌ Sảnh chờ đã full $5/5$ rồi! Vui lòng đợi trận sau nha anh em.")
        return
    lobby_players.append(player)
    current_slots = len(lobby_players)
    await ctx.send(f"✅ **{player.display_name}** đã đặt gạch thành công! Sảnh chờ hiện tại: `{current_slots}/5`")
    mentions_list = ", ".join([p.mention for p in lobby_players])
    await ctx.send(f"👥 **Đội hình hiện tại:** {mentions_list}")
    if current_slots == 5:
        await ctx.send(f"🔥 🎉 **SẢNH CHỜ ĐÃ ĐỦ ĐỘI HÌNH!** {mentions_list} bật game lên và chiến ngay thôi nào!!")
        lobby_players = [] 

@bot.command(name="out")
async def out_command(ctx):
    global lobby_players
    player = ctx.author
    if player in lobby_players:
        lobby_players.remove(player)
        await ctx.send(f"🏃‍♂️ **{player.display_name}** đã rút gạch khỏi sảnh chờ. Sảnh hiện tại: `{len(lobby_players)}/5`")
    else:
        await ctx.send(f"❌ Ông đã có tên trong sảnh đâu mà rút hả {player.mention}!")

@bot.command(name="ganh")
async def ganh_command(ctx):
    # Ép bot quét và nạp lại toàn bộ thành viên thực tế của riêng server này vào cache
    if ctx.guild.chunked is False:
        await ctx.guild.chunk()

    # CHỈ LẤY THÀNH VIÊN ĐANG ONLINE (Tránh xa những ông Offline và không bốc Bot)
    members = [
        member for member in ctx.guild.members 
        if not member.bot and member.status != discord.Status.offline
    ]
    
    # Nếu không quét được ai online (do bot chưa load xong trạng thái hoặc mọi người ẩn danh)
    # Hệ thống sẽ tự động lấy những người vừa nhắn tin gần đây trong server để bù vào
    if not members:
        members = [member for member in ctx.guild.members if not member.bot]

    if not members:
        await ctx.send("Ủa server này không quét được ai hết vậy? Thử lại xem nào!")
        return

    # Bốc ngẫu nhiên một người trong danh sách đang online
    chosen_player = random.choice(members)
    rate = random.randint(0, 150)

    comments = [
        f"Thần rùa hiển linh! Ngôi sao phương xa vừa xem quẻ và phán: Hôm nay **{chosen_player.mention}** sẽ gánh team còng lưng với `{rate}%` công lực! 🧘‍♂️",
        f"Góc cảnh báo: Tỉ lệ bóp team, thả tạ của **{chosen_player.mention}** hôm nay lên tới `{rate}%`. Anh em né gấp kẻo tụt rank! Tạ nặng quá!",
        f"Nhân phẩm check: Hôm nay **{chosen_player.mention}** có `{rate}%` cơ hội đạt danh hiệu MVP. Không win hơi phí!",
        f"Trận này **{chosen_player.mention}** gánh được `{rate}%` trận đấu, còn lại ăn hại là chính chứ không làm ăn được gì."
    ]
    
    await ctx.send(random.choice(comments))

@bot.command(name="game")
async def game_command(ctx):
    chosen_game = random.choice(game_list)
    await ctx.send(f"🎲 Đang xoay vòng quay may mắn... Cả lũ bớt cãi nhau nha!")
    await ctx.send(f"🎯 **Hôm nay cả sảnh sẽ chơi game:**  🏆 ` {chosen_game} ` 🏆")

@bot.command(name="daily")
async def daily_command(ctx):
    player_id = ctx.author.id
    if player_id in has_claimed_daily:
        await ctx.send(f"❌ {ctx.author.mention} ơi, hôm nay ông đã nhận xu rồi! Mai quay lại nhé.")
        return
    gift_coins = random.randint(100, 500)
    player_points[player_id] = player_points.get(player_id, 0) + gift_coins
    has_claimed_daily.add(player_id)
    await ctx.send(f"💰 **{ctx.author.display_name}** đã điểm danh thành công và nhận được `{gift_coins}` Xu sảnh chờ! (Tài sản hiện tại: `{player_points[player_id]}` Xu)")

@bot.command(name="dice")
async def dice_command(ctx, bet_amount: int = None):
    player_id = ctx.author.id
    current_balance = player_points.get(player_id, 0)
    if bet_amount is None or bet_amount <= 0:
        await ctx.send(f"❓ Vui lòng nhập số xu muốn cược! Ví dụ: `!dice 50`")
        return
    if current_balance < bet_amount:
        await ctx.send(f"❌ Ông không đủ xu rồi! Số dư hiện tại chỉ có `{current_balance}` Xu. Gõ `!daily` để kiếm thêm nhé.")
        return
    bot_score = random.randint(1, 6)
    player_score = random.randint(1, 6)
    await ctx.send(f"🎲 **Bot Tú** đổ ra: ` {bot_score} ` | 🎲 **{ctx.author.display_name}** đổ ra: ` {player_score} `")
    if player_score > bot_score:
        player_points[player_id] += bet_amount
        await ctx.send(f"🎉 **THẮNG RỒI!** Bạn ăn được `{bet_amount}` xu! Số dư mới: `{player_points[player_id]}` Xu.")
    elif player_score < bot_score:
        player_points[player_id] -= bet_amount
        await ctx.send(f"😭 **THUA RỒI!** Bạn mất trắng `{bet_amount}` xu! Số dư mới: `{player_points[player_id]}` Xu.")
    else:
        await ctx.send(f"🤝 **HÒA NHAU!** Huề vốn, không ai mất xu nào. Số dư giữ nguyên: `{player_points[player_id]}` Xu.")

# 5. Chạy Bot bằng Token của bạn
TOKEN = "bot-token"

bot.run(TOKEN)
