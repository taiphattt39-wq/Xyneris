import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, UTC, timedelta
import os

TOKEN = os.getenv("TOKEN")
BOT_NAME = "Xyneris"
antinuke_enabled = True
nuke_track = {}
user_lang = {}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree

LANG = {
    "vi": {"set": "✅ Đã đặt ngôn ngữ: Tiếng Việt", "antinuke_on": "🛡️ AntiNuke ĐÃ BẬT", "antinuke_off": "🚫 AntiNuke ĐÃ TẮT"},
    "en": {"set": "✅ Language set to: English", "antinuke_on": "🛡️ AntiNuke ENABLED", "antinuke_off": "🚫 AntiNuke DISABLED"},
    "zh": {"set": "✅ 语言已设置: 中文", "antinuke_on": "🛡️ 防破坏系统 已启用", "antinuke_off": "🚫 防破坏系统 已关闭"},
    "ja": {"set": "✅ 言語: 日本語 に設定", "antinuke_on": "🛡️ アンチニューク 有効", "antinuke_off": "🚫 アンチニューク 無効"},
    "ko": {"set": "✅ 언어: 한국어로 설정됨", "antinuke_on": "🛡️ 안티누크 활성화", "antinuke_off": "🚫 안티누크 비활성화"},
    "fr": {"set": "✅ Langue: Français", "antinuke_on": "🛡️ Anti-Nucléage ACTIVÉ", "antinuke_off": "🚫 Anti-Nucléage DÉSACTIVÉ"},
    "de": {"set": "✅ Sprache: Deutsch", "antinuke_on": "🛡️ Anti-Nuke AKTIV", "antinuke_off": "🚫 Anti-Nuke DEAKTIVIERT"},
    "es": {"set": "✅ Idioma: Español", "antinuke_on": "🛡️ Anti-Nuke ACTIVADO", "antinuke_off": "🚫 Anti-Nuke DESACTIVADO"},
    "pt": {"set": "✅ Idioma: Português", "antinuke_on": "🛡️ Anti-Nuke ATIVADO", "antinuke_off": "🚫 Anti-Nuke DESATIVADO"},
    "ru": {"set": "✅ Язык: Русский", "antinuke_on": "🛡️ Анти-Нукер ВКЛЮЧЕН", "antinuke_off": "🚫 Анти-Нукер ОТКЛЮЧЕН"},
    "th": {"set": "✅ ตั้งค่าภาษา: ไทย", "antinuke_on": "🛡️ เปิดใช้งานระบบป้องกัน", "antinuke_off": "🚫 ปิดใช้งานระบบป้องกัน"},
    "id": {"set": "✅ Bahasa: Indonesia", "antinuke_on": "🛡️ Anti-Nuke AKTIF", "antinuke_off": "🚫 Anti-Nuke NONAKTIF"}
}

def get_lang_id(interaction):
    return user_lang.get(str(interaction.user.id), "vi")

async def check_nuke(guild, action):
    if not antinuke_enabled: return
    async for entry in guild.audit_logs(limit=3, after=datetime.now(UTC)-timedelta(seconds=15)):
        if entry.user.bot: continue
        uid = str(entry.user.id)
        now = datetime.now(UTC)
        if uid not in nuke_track or (now - nuke_track[uid]["time"]).total_seconds() > 15:
            nuke_track[uid] = {"count": 1, "time": now}
        else:
            nuke_track[uid]["count"] += 1
        if nuke_track[uid]["count"] >= 3:
            try: await guild.ban(entry.user, reason=f"AntiNuke: {action}")
            except: pass

@bot.event
async def on_guild_channel_delete(ch): await check_nuke(ch.guild, f"Xóa kênh: {ch.name}")
@bot.event
async def on_guild_role_create(r): await check_nuke(r.guild, f"Tạo vai trò: {r.name}")
@bot.event
async def on_guild_role_delete(r): await check_nuke(r.guild, f"Xóa vai trò: {r.name}")
@bot.event
async def on_member_ban(g, u): await check_nuke(g, f"Cấm: {u}")

@tree.command(name="antinuke", description="Bật/Tắt chống nuke")
@app_commands.checks.has_permissions(administrator=True)
async def antinuke_cmd(interaction: discord.Interaction, trang_thai: str):
    global antinuke_enabled
    lt = trang_thai.lower()
    if lt in ["bật", "on"]:
        antinuke_enabled = True
        await interaction.response.send_message(LANG[get_lang_id(interaction)]["antinuke_on"], ephemeral=True)
    elif lt in ["tắt", "off"]:
        antinuke_enabled = False
        await interaction.response.send_message(LANG[get_lang_id(interaction)]["antinuke_off"], ephemeral=True)
    else:
        status = "✅ BẬT" if antinuke_enabled else "❌ TẮT"
        await interaction.response.send_message(f"Trạng thái: {status}\nNhập: bật / tắt", ephemeral=True)

@antinuke_cmd.autocomplete("trang_thai")
async def antinuke_auto(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name="✅ Bật", value="bật"), app_commands.Choice(name="❌ Tắt", value="tắt")]

@antinuke_cmd.error
async def err(interaction, e):
    await interaction.response.send_message("❌ Chỉ Quản Trị Viên dùng được!", ephemeral=True)

@tree.command(name="language", description="Chọn ngôn ngữ")
async def lang_cmd(interaction: discord.Interaction, ngon_ngu: str):
    if ngon_ngu not in LANG:
        await interaction.response.send_message("❌ Mã không hợp lệ!", ephemeral=True)
        return
    user_lang[str(interaction.user.id)] = ngon_ngu
    await interaction.response.send_message(LANG[ngon_ngu]["set"], ephemeral=True)

@lang_cmd.autocomplete("ngon_ngu")
async def lang_auto(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="🇻🇳 Tiếng Việt", value="vi"),
        app_commands.Choice(name="🇬🇧 English", value="en"),
        app_commands.Choice(name="🇨🇳 中文", value="zh"),
        app_commands.Choice(name="🇯🇵 日本語", value="ja"),
        app_commands.Choice(name="🇰🇷 한국어", value="ko"),
        app_commands.Choice(name="🇫🇷 Français", value="fr"),
        app_commands.Choice(name="🇩🇪 Deutsch", value="de"),
        app_commands.Choice(name="🇪🇸 Español", value="es"),
        app_commands.Choice(name="🇧🇷 Português", value="pt"),
        app_commands.Choice(name="🇷🇺 Русский", value="ru"),
        app_commands.Choice(name="🇹🇭 ไทย", value="th"),
        app_commands.Choice(name="🇮🇩 Indonesia", value="id"),
    ]

@bot.event
async def on_ready():
    print(f"✅ {BOT_NAME} ĐÃ LÊN! — {bot.user}")
    synced = await tree.sync()
    print(f"✅ Đồng bộ {len(synced)} lệnh")

if __name__ == "__main__":
    bot.run(TOKEN)
