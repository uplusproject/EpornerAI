import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ==================== 配置区域 ====================
BOT_TOKEN = "9226294111:AAGae-n4UoF_xXlhPv1wqoZcrFei-j7wlVY"          # ← 请替换成你的 Token
API_BASE = "https://www.eporner.com/api/v2/video"
PER_PAGE = 8
# =================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== 关键词映射表（支持模糊匹配） ====================
KEYWORD_MAP = {
    # 类型
    "近親相姦": "incest", "近亲相奸": "incest", "乱伦": "incest", "亂倫": "incest",
    "근친강간": "incest", "근친": "incest", "incesto": "incest",
    "潮吹き": "squirting", "潮吹": "squirting", "스퀴팅": "squirting", "물싸": "squirting",
    "中出": "creampie", "中出し": "creampie", "内射": "creampie", "질내사정": "creampie",
    "人妻": "married woman", "熟女": "mature", "기혼여성": "married woman", "아줌마": "mature",
    "巨乳": "big tits", "爆乳": "huge tits", "大奶": "big tits", "큰가슴": "big tits", "거유": "big tits",
    "学生": "schoolgirl", "女学生": "schoolgirl", "JK": "schoolgirl", "학생": "schoolgirl", "여학생": "schoolgirl",
    "按摩": "massage", "マッサージ": "massage", "마사지": "massage",
    "女同": "lesbian", "百合": "lesbian", "レズ": "lesbian", "레즈비언": "lesbian",
    "口交": "blowjob", "フェラ": "blowjob", "口爆": "blowjob", "펠라치오": "blowjob",
    "肛交": "anal", "アナル": "anal", "애널": "anal",
    "日本": "japanese", "日本人": "japanese", "日系": "japanese", "일본": "japanese",
    "韩国": "korean", "韓女": "korean", "한국": "korean",
    "印度": "indian", "インド": "indian", "인도": "indian",
    "中国": "chinese", "中國": "chinese", "중국": "chinese",
    "泰国": "thai", "タイ": "thai", "태국": "thai",

    # 女优模糊匹配
    "三上悠亜": "Yua Mikami", "三上悠亚": "Yua Mikami", "三上": "Yua Mikami", "悠亜": "Yua Mikami", "悠亚": "Yua Mikami",
    "楪カレン": "Karen Yuzuriha", "カレン": "Karen Yuzuriha", "楪": "Karen Yuzuriha",
    "明日花キララ": "Kirara Asuka", "明日花绮罗": "Kirara Asuka", "明日花": "Kirara Asuka", "キララ": "Kirara Asuka",
    "橋本ありな": "Arina Hashimoto", "桥本有菜": "Arina Hashimoto", "橋本": "Arina Hashimoto", "ありな": "Arina Hashimoto",
    "天使もえ": "Moe Amatsuka", "天使萌": "Moe Amatsuka", "天使": "Moe Amatsuka", "もえ": "Moe Amatsuka",
    "葵つかさ": "Tsukasa Aoi", "葵司": "Tsukasa Aoi", "葵": "Tsukasa Aoi", "つかさ": "Tsukasa Aoi",
    "深田えいみ": "Eimi Fukada", "深田咏美": "Eimi Fukada", "深田": "Eimi Fukada", "えいみ": "Eimi Fukada",
    "波多野結衣": "Yui Hatano", "波多野结衣": "Yui Hatano", "波多野": "Yui Hatano", "結衣": "Yui Hatano",
    "上原亜衣": "Ai Uehara", "上原亚衣": "Ai Uehara", "上原": "Ai Uehara", "亜衣": "Ai Uehara",
    "佐倉絆": "Kizuna Sakura", "佐仓绊": "Kizuna Sakura", "佐倉": "Kizuna Sakura", "絆": "Kizuna Sakura",
    "希崎ジェシカ": "Jessica Kizaki", "希崎杰西卡": "Jessica Kizaki", "希崎": "Jessica Kizaki", "ジェシカ": "Jessica Kizaki",
    "小島みなみ": "Minami Kojima", "小岛南": "Minami Kojima", "小島": "Minami Kojima", "みなみ": "Minami Kojima",
    "鈴村あいり": "Airu Suzumura", "铃村爱里": "Airu Suzumura", "鈴村": "Airu Suzumura", "あいり": "Airu Suzumura",
    "美谷朱里": "Akari Mitani", "美谷": "Akari Mitani", "朱里": "Akari Mitani",
    "相沢みなみ": "Minami Aizawa", "相沢": "Minami Aizawa",
    "楓カレン": "Karen Kaede", "楓": "Karen Kaede",
    "明里つむぎ": "Tsumugi Akari", "明里": "Tsumugi Akari", "つむぎ": "Tsumugi Akari",
    "紗倉まな": "Mana Sakura", "纱仓真菜": "Mana Sakura", "紗倉": "Mana Sakura", "まな": "Mana Sakura",
    "戸田真琴": "Makoto Toda", "户田真琴": "Makoto Toda", "戸田": "Makoto Toda", "真琴": "Makoto Toda",
    "七沢みあ": "Mia Nanasawa", "七泽米亚": "Mia Nanasawa", "七沢": "Mia Nanasawa", "みあ": "Mia Nanasawa",
    "初川みなみ": "Minami Hatsukawa", "初川": "Minami Hatsukawa",
    "神宮寺ナオ": "Nao Jinguji", "神宫寺奈绪": "Nao Jinguji", "神宮寺": "Nao Jinguji", "ナオ": "Nao Jinguji",
    "君島みお": "Mio Kimijima", "君岛美绪": "Mio Kimijima", "君島": "Mio Kimijima", "みお": "Mio Kimijima",
    "篠田ゆう": "Yu Shinoda", "筱田优": "Yu Shinoda", "篠田": "Yu Shinoda", "ゆう": "Yu Shinoda",
    "美咲かんな": "Kanna Misaki", "美咲": "Kanna Misaki", "かんな": "Kanna Misaki",
    "高橋しょう子": "Shoko Takahashi", "高桥圣子": "Shoko Takahashi", "高橋": "Shoko Takahashi",

    # 其他
    "颜射": "facial", "顔射": "facial", "안면사정": "facial",
    "足交": "footjob", "足コキ": "footjob",
    "群交": "gangbang", "乱交": "orgy",
    "NTR": "ntr", "绿帽": "ntr", "寝取られ": "ntr",
    "露出": "exhibitionist", "户外": "public",
    "捆绑": "bondage", "SM": "bdsm", "調教": "bdsm",
}

def translate_keyword(text: str) -> str:
    text = text.strip()
    if text in KEYWORD_MAP:
        return KEYWORD_MAP[text]
    for key, value in KEYWORD_MAP.items():
        if key in text:
            return value
    return text

def call_eporner_api(endpoint: str, params: dict = None):
    url = f"{API_BASE}/{endpoint}/"
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None

def format_video_caption(video: dict) -> str:
    title = video.get("title", "No Title")
    length = video.get("length_min", "Unknown")
    views = video.get("views", 0)
    rate = video.get("rate", "0")
    url = video.get("url", "")
    embed = video.get("embed", "")

    caption = (
        f"🎬 <b>{title}</b>\n\n"
        f"⏱ Duration: {length}\n"
        f"👁 Views: {views:,}\n"
        f"⭐ Rating: {rate}\n\n"
        f"🔗 <a href='{url}'>Watch Page</a>\n"
        f"📺 <a href='{embed}'>Embed Player</a>"
    )
    return caption

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🔥 Latest"), KeyboardButton("🏆 Most Popular")],
        [KeyboardButton("📅 This Week"), KeyboardButton("📆 This Month")],
        [KeyboardButton("⭐ Top Rated"), KeyboardButton("🎲 Random")],
        [KeyboardButton("👩 Actresses"), KeyboardButton("📂 Categories")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_actress_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("三上悠亜", callback_data="search|Yua Mikami"),
            InlineKeyboardButton("楪カレン", callback_data="search|Karen Yuzuriha"),
        ],
        [
            InlineKeyboardButton("明日花キララ", callback_data="search|Kirara Asuka"),
            InlineKeyboardButton("橋本ありな", callback_data="search|Arina Hashimoto"),
        ],
        [
            InlineKeyboardButton("天使もえ", callback_data="search|Moe Amatsuka"),
            InlineKeyboardButton("葵つかさ", callback_data="search|Tsukasa Aoi"),
        ],
        [
            InlineKeyboardButton("深田えいみ", callback_data="search|Eimi Fukada"),
            InlineKeyboardButton("波多野結衣", callback_data="search|Yui Hatano"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_genre_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Japanese", callback_data="search|japanese"),
            InlineKeyboardButton("Incest", callback_data="search|incest"),
        ],
        [
            InlineKeyboardButton("Squirting", callback_data="search|squirting"),
            InlineKeyboardButton("Creampie", callback_data="search|creampie"),
        ],
        [
            InlineKeyboardButton("Big Tits", callback_data="search|big tits"),
            InlineKeyboardButton("Schoolgirl", callback_data="search|schoolgirl"),
        ],
        [
            InlineKeyboardButton("Married Woman", callback_data="search|married woman"),
            InlineKeyboardButton("Lesbian", callback_data="search|lesbian"),
        ],
        [
            InlineKeyboardButton("Massage", callback_data="search|massage"),
            InlineKeyboardButton("Anal", callback_data="search|anal"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome to Eporner Video Search Bot\n\n"
        "📌 How to use / 使い方 / 使用方法 / 사용 방법：\n\n"
        "🇺🇸 English:\n"
        "• Just type any keyword to search\n"
        "• Use the buttons below for quick access\n\n"
        "🇯🇵 日本語：\n"
        "• キーワードを入力するだけで検索できます\n"
        "• 下のボタンで素早く検索\n\n"
        "🇹🇼 繁體中文：\n"
        "• 直接輸入關鍵詞即可搜尋\n"
        "• 點擊下方按鈕快速瀏覽\n\n"
        "🇰🇷 한국어：\n"
        "• 키워드를 입력하면 바로 검색됩니다\n"
        "• 아래 버튼으로 빠르게 이용하세요\n\n"
        "💡 Supports Chinese, Japanese, Korean keywords with auto-translation."
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text in ["🔥 Latest", "🔥 最新视频"]:
        await send_video_list(update, context, query="all", order="latest", page=1)
    elif text in ["🏆 Most Popular", "🏆 全站最热"]:
        await send_video_list(update, context, query="all", order="most-popular", page=1)
    elif text in ["📅 This Week", "📅 本周热门"]:
        await send_video_list(update, context, query="all", order="top-weekly", page=1)
    elif text in ["📆 This Month", "📆 本月热门"]:
        await send_video_list(update, context, query="all", order="top-monthly", page=1)
    elif text in ["⭐ Top Rated", "⭐ 高分视频"]:
        await send_video_list(update, context, query="all", order="top-rated", page=1)
    elif text in ["🎲 Random", "🎲 随机推荐"]:
        await send_video_list(update, context, query="all", order="latest", page=1)
    elif text in ["👩 Actresses", "👩 热门女优"]:
        await update.message.reply_text("Select an actress:", reply_markup=get_actress_keyboard())
    elif text in ["📂 Categories", "📂 热门分类"]:
        await update.message.reply_text("Select a category:", reply_markup=get_genre_keyboard())
    else:
        translated = translate_keyword(text)
        await send_video_list(update, context, query=translated, order="latest", page=1)

async def send_video_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          query: str, order: str, page: int):
    params = {
        "query": query,
        "per_page": PER_PAGE,
        "page": page,
        "order": order,
        "thumbsize": "big",
        "gay": 0,
        "lq": 1,
        "format": "json"
    }

    data = call_eporner_api("search", params)

    if not data or "videos" not in data:
        text = "Failed to get data. Please try again later."
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    videos = data["videos"]
    total_pages = data.get("total_pages", 1)
    total_count = data.get("total_count", 0)

    if not videos:
        # 多语言“没有找到视频”提示
        text = (
            "❌ No videos found.\n\n"
            "🇯🇵 動画が見つかりませんでした。\n"
            "🇹🇼 沒有找到相關視頻。\n"
            "🇰🇷 관련 영상을 찾을 수 없습니다.\n\n"
            "💡 Tip / ヒント / 提示 / 팁：\n"
            "Try simpler English keywords like:\n"
            "japanese / incest / squirting / creampie / big tits"
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    header = f"🔍 Search: {query} | Sort: {order}\nTotal: {total_count:,} results | Page {page}/{total_pages}"
    if update.callback_query:
        await update.callback_query.edit_message_text(header)
    else:
        await update.message.reply_text(header)

    for video in videos:
        caption = format_video_caption(video)
        thumb = video.get("default_thumb", {}).get("src")
        try:
            if thumb:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=thumb,
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=caption,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.warning(f"Send failed: {e}")

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page|{query}|{order}|{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page|{query}|{order}|{page+1}"))

    if buttons:
        reply_markup = InlineKeyboardMarkup([buttons])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📄 Page {page} / {total_pages}",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_main":
        await query.edit_message_text("Back to main menu. Type a keyword or use the buttons below.")
        return

    if data.startswith("search|"):
        keyword = data.split("|", 1)[1]
        await send_video_list(update, context, query=keyword, order="latest", page=1)
        return

    if data.startswith("page|"):
        _, search_query, order, page = data.split("|")
        await send_video_list(update, context, query=search_query, order=order, page=int(page))

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()