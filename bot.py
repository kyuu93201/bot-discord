import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random
import asyncio
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help') 

# ==========================================
# CẤU HÌNH TỪ ĐIỂN TỰ ĐỘNG QUÉT THEO TỪ LOẠI
# ==========================================
# Đường dẫn gốc dẫn đến raw file trên GitHub của winstonleedev
BASE_RAW_URL = "https://raw.githubusercontent.com/winstonleedev/tudien/master/"
LOCAL_BACKUP_FILE = "tudien.txt"

# Danh sách các tên file txt phân chia theo Từ Loại tiếng Việt
PART_OF_SPEECH_FILES = [
    "danhtu.txt", "dongtu.txt", "tinhtu.txt", "trangtu.txt", 
    "daitu.txt", "gioitu.txt", "lientu.txt", "thantu.txt",
    "danhtu.txt", "dongtu.txt", "tinhtu.txt", "trangtu.txt" # Phòng hờ trường hợp viết liền không dấu cách
]

# Tập hợp từ vựng cốt lõi mặc định phòng khi mất mạng hoàn toàn
vietnamese_words = {
    "học hành", "hành động", "động lực", "lực lượng", "lượng tử", "tử trận", "trận đấu",
    "đấu giá", "giá cả", "tử vong", "vong mạng", "mạng sống", "sống sót", "sót lại"
}

def clean_and_add_words(text_data):
    """Hàm lọc và nạp từ ghép từ dữ liệu chữ thô"""
    count = 0
    lines = text_data.splitlines()
    for line in lines:
        clean_word = line.strip().lower()
        # Chỉ nhận từ ghép hợp lệ (có dấu cách và độ dài > 2)
        if " " in clean_word and len(clean_word) > 2:
            vietnamese_words.add(clean_word)
            count += 1
    return count

async def load_all_dictionaries():
    """Hàm bất đồng bộ tải và gộp tất cả file từ điển theo từ loại"""
    print("[.] Đang tiến hành quét và tải loạt file từ loại online từ GitHub...")
    all_downloaded_text = []
    total_loaded_online = 0
    
    # Chạy vòng lặp tải từng file từ loại
    for file_name in PART_OF_SPEECH_FILES:
        # Mã hóa khoảng trắng thành %20 để URL không bị lỗi khi gọi requests
        encoded_name = file_name.replace(" ", "%20")
        file_url = f"{BASE_RAW_URL}{encoded_name}"
        
        try:
            # Chạy requests trong executor để tránh làm đứng bot
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(file_url, timeout=5))
            
            if response.status_code == 200 and len(response.text.strip()) > 0:
                words_count = clean_and_add_words(response.text)
                all_downloaded_text.append(response.text)
                total_loaded_online += words_count
                print(f" └── [✓] Đã nạp file từ loại '{file_name}': +{words_count} từ.")
        except Exception:
            # Bỏ qua nếu file đó không tồn tại hoặc lỗi mạng cục bộ file đó
            continue

    # Nếu tải thành công từ online, tiến hành ghi đè bản gộp sao lưu xuống máy
    if total_loaded_online > 0:
        print(f"[+] Tải online hoàn tất! Đã gom được tổng cộng {total_loaded_online} từ từ các file từ loại.")
        try:
            with open(LOCAL_BACKUP_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(all_downloaded_text))
            print(f"[+] Đã sao lưu bản gộp vào file cục bộ '{LOCAL_BACKUP_FILE}'.")
        except Exception as e:
            print(f"[X] Lỗi ghi file sao lưu: {e}")
            
    # Nếu lỗi mạng / GitHub chặn ngay từ đầu -> Đọc file gộp cũ đã lưu trên máy
    else:
        print("[!] Không tải được file online nào. Tiến hành kiểm tra kho sao lưu cục bộ...")
        if os.path.exists(LOCAL_BACKUP_FILE):
            try:
                with open(LOCAL_BACKUP_FILE, "r", encoding="utf-8") as f:
                    local_count = clean_and_add_words(f.read())
                print(f"[+] Khôi phục thành công {local_count} từ vựng từ bản sao lưu '{LOCAL_BACKUP_FILE}'!")
            except Exception as file_err:
                print(f"[X] Lỗi đọc file sao lưu cục bộ: {file_err}")
        else:
            print(f"[!] Không tìm thấy sao lưu cũ. Bot tạm dùng kho dự phòng cơ bản ({len(vietnamese_words)} từ).")

    print(f"[🌐] HỆ THỐNG SẴN SÀNG - Tổng số từ vựng trong bộ nhớ: {len(vietnamese_words)}")

# ==========================================
# CẤU HÌNH VẬT PHẨM GACHA (ĐỘ HIẾM & GIÁ BÁN)
# ==========================================
GACHA_ITEMS = {
    "Common": [
        {"name": "Kiếm Gỗ Mục", "emoji": "🪵", "sell_price": 10},
        {"name": "Cúp Đá Nứt", "emoji": "🪨", "sell_price": 12},
        {"name": "Giày Vải Rách", "emoji": "👟", "sell_price": 15}
    ],
    "Rare": [
        {"name": "Rìu Sắt Sắc Bén", "emoji": "🪓", "sell_price": 50},
        {"name": "Giáp Xích Đồng", "emoji": "🛡️", "sell_price": 65},
        {"name": "Nhẫn Bạc Cổ", "emoji": "💍", "sell_price": 80}
    ],
    "Epic": [
        {"name": "Thần Kiếm Kim Cương", "emoji": "💎", "sell_price": 250},
        {"name": "Trượng Ma Pháp Tối Thượng", "emoji": "🔮", "sell_price": 300},
        {"name": "Cánh Phượng Hoàng", "emoji": "🪶", "sell_price": 450}
    ],
    "Legendary": [
        {"name": "Long Đao Diệt Thế", "emoji": "🐉", "sell_price": 1500},
        {"name": "Vương Miện Thần Linh", "emoji": "👑", "sell_price": 2000},
        {"name": "Khiên Vạn Năng Aegis", "emoji": "🔱", "sell_price": 2500}
    ]
}
GACHA_COST = 50 

# ==========================================
# QUẢN LÝ DATABASE JSON (KINH TẾ & KHO ĐỒ)
# ==========================================
ECONOMY_FILE = "kinhte.json"
INVENTORY_FILE = "khodo.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_money(user_id):
    data = load_json(ECONOMY_FILE)
    return data.get(str(user_id), 100) 

def add_money(user_id, amount):
    data = load_json(ECONOMY_FILE)
    str_id = str(user_id)
    data[str_id] = data.get(str_id, 100) + amount
    save_json(ECONOMY_FILE, data)
    return data[str_id]

# ==========================================
# CƠ CHẾ NÚT BẤM ĐƯỜNG LINK SẢNH CHỜ URL
# ==========================================
class LobbyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="Tham Gia Sảnh Chờ Ngay 🎮", 
            url="https://discord.gg/YOUR_INVITE_LINK", 
            style=discord.ButtonStyle.link
        ))

async def check_bridge_file():
    await bot.wait_until_ready()
    
    # 🔴 ĐIỀN ID KÊNH CHAT THẬT CỦA BẠN VÀO ĐÂY ĐỂ TRÁNH LỖI 'NoneType'
    TARGET_CHANNEL_ID = 1439470744328339558
    
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel is None:
        print(f"[X] Cảnh báo: Chưa tìm thấy kênh chat ID {TARGET_CHANNEL_ID}. Vui lòng kiểm tra lại cấu hình!")
    
    while not bot.is_closed():
        if os.path.exists("message.txt"):
            try:
                with open("message.txt", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content and channel is not None:
                    if content == "ONLINE_SIGNAL":
                        embed = discord.Embed(
                            title="🎮 SẢNH CHỜ MINECRAFT ĐÃ ONLINE",
                            description="**Trạng thái:** Đang mở cửa tìm đồng đội chơi Minecraft Mèo Béo!\n\n🟢 ⚪ ⚪ ⚪ ⚪  `[1/5 Slot]`",
                            color=0x2ecc71
                        )
                        await channel.send(embed=embed, view=LobbyView())
                    else:
                        await channel.send(content)
                os.remove("message.txt")
            except Exception as e:
                print(f"Lỗi đọc file bridge: {e}")
        await asyncio.sleep(1)

# ==========================================
# 📝 CHỨC NĂNG: TRÒ CHƠI NỐI TỪ TIẾNG VIỆT
# ==========================================
noitu_games = {}

@bot.command(name="ntbot")
async def play_with_bot(ctx):
    channel_id = ctx.channel.id
    if channel_id in noitu_games:
        await ctx.send("🎮 Kênh này đang có một trận đấu diễn ra rồi!")
        return
    start_word = random.choice(list(vietnamese_words))
    noitu_games[channel_id] = {"type": "bot", "player": ctx.author.id, "last_word": start_word, "used_words": {start_word}}
    await ctx.send(embed=discord.Embed(title="🤖 ĐẤU NỐI TỪ VỚI BOT TÚ", description=f"Từ của Bot: **{start_word}**\n👉 Lượt của {ctx.author.mention}, nối tiếp chữ: `{start_word.split()[-1]}` (30s suy nghĩ)", color=0x3498db))
    await start_timeout_check(ctx, channel_id)

@bot.command(name="ntpvp")
async def play_pvp(ctx, opponent: discord.Member = None):
    channel_id = ctx.channel.id
    if channel_id in noitu_games: return
    if opponent is None or opponent.bot or opponent == ctx.author:
        await ctx.send("❌ Cú pháp: `!ntpvp @Tên_Người_Chơi` để thách đấu!")
        return
    await ctx.send(f"⚔️ {opponent.mention}! Bạn được {ctx.author.mention} mời đấu nối từ ăn tiền. Gõ `yes` để nhận hoặc `no` để từ chối (30s)!")
    
    def check(m): return m.channel.id == channel_id and m.author.id == opponent.id and m.content.lower() in ["yes", "no"]
    try:
        reply = await bot.wait_for("message", check=check, timeout=30)
        if reply.content.lower() == "no": return await ctx.send("🛑 Lời mời bị từ chối!")
    except asyncio.TimeoutError: return await ctx.send("⏰ Hết thời gian chờ thách đấu!")

    start_word = random.choice(list(vietnamese_words))
    players = [ctx.author.id, opponent.id]
    random.shuffle(players)
    noitu_games[channel_id] = {"type": "pvp", "players": players, "turn": 0, "last_word": start_word, "used_words": {start_word}}
    await ctx.send(embed=discord.Embed(title="⚔️ TRẬN ĐẤU PVP BẮT ĐẦU", description=f"Từ xuất phát: **{start_word}**\n👉 Lượt của: <@{players[0]}>, nối tiếp chữ: `{start_word.split()[-1]}`", color=0xe74c3c))
    await start_timeout_check(ctx, channel_id)

@bot.command(name="huytran")
async def force_stop_game(ctx):
    if ctx.channel.id in noitu_games:
        del noitu_games[ctx.channel.id]
        await ctx.send("🛑 Đã hủy trận đấu nối từ thành công!")

# ==========================================
# 🎰 CHỨC NĂNG: GACHA - KHO ĐỒ - BÁN ĐỒ
# ==========================================
@bot.command(name="gacha")
async def roll_gacha(ctx):
    user_id = ctx.author.id
    if get_money(user_id) < GACHA_COST:
        return await ctx.send(f"❌ Không đủ tiền! Cần `{GACHA_COST}$` để quay (Bạn có: `{get_money(user_id)}$`)")
    
    add_money(user_id, -GACHA_COST)
    rate = random.random() * 100
    rarity = "Legendary" if rate <= 3 else "Epic" if rate <= 15 else "Rare" if rate <= 40 else "Common"
    chosen = random.choice(GACHA_ITEMS[rarity])
    
    inv = load_json(INVENTORY_FILE)
    item_id = str(random.randint(100000, 999999))
    new_item = {"id": item_id, "name": chosen["name"], "emoji": chosen["emoji"], "rarity": rarity, "sell_price": chosen["sell_price"]}
    if str(user_id) not in inv: inv[str(user_id)] = []
    inv[str(user_id)].append(new_item)
    save_json(INVENTORY_FILE, inv)
    
    emb = discord.Embed(title="🎰 KẾT QUẢ QUAY GACHA", color=0xf1c40f if rarity=="Legendary" else 0x9b59b6 if rarity=="Epic" else 0x3498db)
    emb.add_field(name="🎁 Nhận được:", value=f"{chosen['emoji']} **{chosen['name']}** `[{rarity}]` (ID: `{item_id}`)", inline=False)
    emb.set_footer(text=f"Giá thanh lý: {chosen['sell_price']}$ | Ví còn lại: {get_money(user_id)}$")
    await ctx.send(embed=emb)

@bot.command(name="khodo")
async def view_inventory(ctx):
    inv = load_json(INVENTORY_FILE)
    items = inv.get(str(ctx.author.id), [])
    if not items: return await ctx.send("🎒 Rương đồ của bạn đang trống rỗng!")
    
    txt = "".join([f"▪️ `{i['id']}` | {i['emoji']} **{i['name']}** - `[{i['rarity']}]` ({i['sell_price']}$)\n" for i in items[:20]])
    await ctx.send(embed=discord.Embed(title=f"🎒 KHO ĐỒ ẢO CỦA {ctx.author.name.upper()}", description=txt, color=0x2ecc71))

@bot.command(name="ban")
async def sell_item(ctx, item_id: str = None):
    if not item_id: return await ctx.send("❌ Cú pháp: `!ban [Mã_ID_Vật_Phẩm]`")
    inv = load_json(INVENTORY_FILE)
    user_items = inv.get(str(ctx.author.id), [])
    
    for item in user_items:
        if item["id"] == item_id:
            user_items.remove(item)
            save_json(INVENTORY_FILE, inv)
            add_money(ctx.author.id, item["sell_price"])
            return await ctx.send(f"✅ Đã bán {item['emoji']} **{item['name']}**, nhận lại **+{item['sell_price']}$**.")
    await ctx.send("❌ Không tìm thấy mã ID vật phẩm này trong kho đồ!")

# ==========================================
# 🏛️ CHỨC NĂNG: CHỢ ĐEN ĐẤU GIÁ (AUCTION)
# ==========================================
active_auctions = {}

@bot.command(name="daugia")
async def start_auction(ctx, item_id: str = None, start_price: int = None):
    if not item_id or not start_price or start_price <= 0:
        return await ctx.send("❌ Cú pháp: `!daugia [Mã_ID] [Giá_Khởi_Điểm]`")
    
    channel_id = ctx.channel.id
    if channel_id in active_auctions: return await ctx.send("❌ Kênh này đang có đấu giá rồi!")
    
    inv = load_json(INVENTORY_FILE)
    user_items = inv.get(str(ctx.author.id), [])
    found = next((i for i in user_items if i["id"] == item_id), None)
    if not found: return await ctx.send("❌ Vật phẩm không có trong kho!")
    
    user_items.remove(found)
    save_json(INVENTORY_FILE, inv)
    
    active_auctions[channel_id] = {"item": found, "seller": ctx.author.id, "highest_bid": start_price, "highest_bidder": None}
    emb = discord.Embed(title="🏛️ SÀN ĐẤU GIÁ MỞ CỬA", description=f"Vật phẩm: {found['emoji']} **{found['name']}**\nGiá khởi điểm: **{start_price}$**\nGõ `!tra [Số_Tiền]` để mua đấu giá!", color=0xe67e22)
    emb.set_footer(text="Đếm ngược 45 giây chốt sổ...")
    await ctx.send(embed=emb)
    
    await asyncio.sleep(45)
    auction = active_auctions.pop(channel_id, None)
    if not auction: return
    
    if not auction["highest_bidder"]:
        inv = load_json(INVENTORY_FILE)
        if str(auction["seller"]) not in inv: inv[str(auction["seller"])] = []
        inv[str(auction["seller"])].append(auction["item"])
        save_json(INVENTORY_FILE, inv)
        await ctx.send(f"🛑 Đấu giá kết thúc, không ai mua! Trả lại {found['name']} cho chủ cũ.")
    else:
        inv = load_json(INVENTORY_FILE)
        buyer_id = str(auction["highest_bidder"])
        if buyer_id not in inv: inv[buyer_id] = []
        inv[buyer_id].append(auction["item"])
        save_json(INVENTORY_FILE, inv)
        add_money(auction["seller"], auction["highest_bid"])
        await ctx.send(f"🎉 **ĐÃ CHỐT ĐƠN!** <@{buyer_id}> sở hữu thành công {found['name']} với giá **{auction['highest_bid']}$**!")

@bot.command(name="tra")
async def bid_item(ctx, price: int = None):
    auction = active_auctions.get(ctx.channel.id)
    if not auction: return await ctx.send("❌ Không có phiên đấu giá nào đang chạy!")
    if ctx.author.id == auction["seller"]: return
    if not price or price <= auction["highest_bid"]: return await ctx.send(f"❌ Phải trả giá cao hơn giá hiện tại ({auction['highest_bid']}$)")
    if get_money(ctx.author.id) < price: return await ctx.send("❌ Không đủ tiền mặt!")
    
    if auction["highest_bidder"]: add_money(auction["highest_bidder"], auction["highest_bid"])
    add_money(ctx.author.id, -price)
    auction["highest_bid"] = price
    auction["highest_bidder"] = ctx.author.id
    await ctx.send(f"🔥 **MỨC GIÁ MỚI!** {ctx.author.mention} đặt giá sàn **{price}$**!")

# ==========================================
# ⚙️ HỆ THỐNG XỬ LÝ SỰ KIỆN VÀ LƯỢT CHƠI PHỤ TRỢ
# ==========================================
async def start_timeout_check(ctx, channel_id):
    if channel_id not in noitu_games: return
    game = noitu_games[channel_id]
    word = game["last_word"]
    await asyncio.sleep(30)
    if channel_id in noitu_games and noitu_games[channel_id]["last_word"] == word:
        if game["type"] == "bot": await ctx.send(f"⏰ Hết giờ! <@{game['player']}> suy nghĩ quá lâu nên bị xử thua!")
        else:
            w = game["players"][1 - game["turn"]]; l = game["players"][game["turn"]]
            await ctx.send(f"⏰ Hết giờ! <@{l}> thua cuộc. <@{w}> nhận thưởng **+100$**!")
            add_money(w, 100)
        del noitu_games[channel_id]

@bot.event
async def on_message(message):
    if message.author.bot: return
    game = noitu_games.get(message.channel.id)
    if game:
        inp = message.content.strip().lower()
        splt = inp.split()
        is_turn = (game["type"] == "bot" and message.author.id == game["player"]) or (game["type"] == "pvp" and message.author.id == game["players"][game["turn"]])
        
        if is_turn and len(splt) >= 2:
            if splt[0] != game["last_word"].split()[-1]: return
            
            if inp not in vietnamese_words or inp in game["used_words"]:
                await message.reply("❌ Từ ngữ bị trùng hoặc không có trong từ điển tiếng Việt chuẩn! Bạn bị xử thua cuộc!")
                if game["type"] == "pvp":
                    w = game["players"][0] if game["players"][0] != message.author.id else game["players"][1]
                    add_money(w, 100)
                    await message.channel.send(f"🏆 <@{w}> giành chiến thắng trận đấu PvP và nhận **+100$**!")
                del noitu_games[message.channel.id]
                return
            
            game["last_word"] = inp; game["used_words"].add(inp)
            await message.add_reaction("✅")
            nxt = splt[-1]
            
            if game["type"] == "bot":
                await asyncio.sleep(1)
                bots = [w for w in vietnamese_words if w.split()[0] == nxt and w not in game["used_words"]]
                if not bots:
                    add_money(message.author.id, 50)
                    await message.channel.send(f"🎉 **Bot Tú chịu thua rồi!** {message.author.mention} thắng trận nhận **+50$**!")
                    del noitu_games[message.channel.id]
                    return
                bw = random.choice(bots); game["last_word"] = bw; game["used_words"].add(bw)
                await message.channel.send(f"🤖 Bot Tú nối từ: **{bw}**\n👉 Lượt của bạn, nối chữ: `{bw.split()[-1]}`")
            else:
                game["turn"] = 1 - game["turn"]
                await message.channel.send(f"⏳ Đến lượt <@{game['players'][game['turn']]}>, nối chữ: `{nxt}`")
            await start_timeout_check(message, message.channel.id)
            return
            
    await bot.process_commands(message)

# ==========================================
# 🤖 LỆNH MENU HELP HIỂN THỊ CHỨC NĂNG
# ==========================================
@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(title="🤖 DANH SÁCH CÁC CÂU LỆNH CÓ THỂ DÙNG & CHỨC NĂNG", description="Dưới đây là bảng hướng dẫn sử dụng các tính năng của Bot Tú. Hãy gõ đúng cú pháp ngoài kênh chat để trải nghiệm nhé!", color=0x2ecc71)
    embed.add_field(name="📝 TRÒ CHƠI NỐI TỪ", value="• `!ntbot` : Bắt đầu chơi nối từ với Bot Tú (Thắng nhận 50$).\n• `!ntpvp @Tên_Người_Chơi` : Thách đấu nối từ ăn tiền với bạn bè (Thắng nhận 100$).\n• `!huytran` : Hủy trận đấu nối từ đang chơi ở kênh hiện tại.", inline=False)
    embed.add_field(name="🎰 VẬT PHẨM VÀ KINH TẾ", value="• `!gacha` : Quay báu vật ngẫu nhiên theo độ hiếm (Tốn 50$ / lượt).\n• `!khodo` : Mở xem tất cả hòm đồ ảo kèm mã số (ID) vật phẩm bạn đang có.\n• `!ban [Mã_ID_Vật_Phẩm]` : Bán nhanh món đồ trong kho của bạn cho Shop hệ thống để lấy tiền mặt.", inline=False)
    embed.add_field(name="🏛️ SÀN ĐẤU GIÁ GIỮA NGƯỜI CHƠI", value="• `!daugia [Mã_ID] [Giá_Khởi_Điểm]` : Treo vật phẩm lên sàn chợ đen trong 45 giây để cả Server tranh mua.\n• `!tra [Số_Tiền]` : Đặt mức tiền cao hơn giá sàn hiện tại để tham gia đấu giá mua đạo cụ.", inline=False)
    if bot.user.avatar: embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"[+] Bot Tú Online! Đã nạp xong toàn bộ kho từ vựng.")
    bot.loop.create_task(check_bridge_file())

# DÁN TOKEN CỦA BẠN VÀO ĐÂY ĐỂ CHẠY
bot.run("bot-token")