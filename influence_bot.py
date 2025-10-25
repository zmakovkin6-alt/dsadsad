# influence_bot.py
import os
import json
from typing import Dict, Any, List, Optional
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    filters, ConversationHandler
)

# ========== Настройки ==========
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATA_DIR = "bot_data"  # папка для хранения данных пользователей

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ========== Константы диалога (Conversation) ==========
(
    A_USERNAME,
    A_FOLLOWERS,
    A_AVG_LIKES,
    A_AVG_COMMENTS,
    A_POSTS_PER_WEEK,
    A_WEEKS_ACTIVE,
    A_TOTAL_WEEKS,
    A_STORIES,
    A_VISUAL_STYLE,
    A_IA_PERCENT,
    A_MORE_ACCOUNTS,
) = range(11)

# ========== Утилиты хранения ==========
def data_path(chat_id: int) -> str:
    return os.path.join(DATA_DIR, f"data_{chat_id}.json")

def load_chat_data(chat_id: int) -> Dict[str, Any]:
    path = data_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"accounts": {}, "order": []}

def save_chat_data(chat_id: int, data: Dict[str, Any]):
    path = data_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== Математика метрик ==========
def compute_ER(followers: int, avg_likes: float, avg_comments: float) -> Optional[float]:
    if not followers or followers <= 0:
        return None
    return (avg_likes + avg_comments) / followers * 100.0

def compute_IS(weeks_active: float, total_weeks: float) -> Optional[float]:
    if not total_weeks or total_weeks <= 0:
        return None
    return (weeks_active / total_weeks) * 100.0

def normalize_VS(vs_rating: float) -> float:
    return max(0.0, min(5.0, vs_rating)) / 5.0 * 100.0

def compute_I(er: Optional[float], is_: Optional[float], ia: Optional[float], vs_pct: float) -> Optional[float]:
    a = er if er is not None else 0.0
    b = is_ if is_ is not None else 0.0
    c = ia if ia is not None else 0.0
    d = vs_pct
    return 0.4 * a + 0.3 * b + 0.2 * c + 0.1 * d

# ========== Команды ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "Привет! Я бот-аналитик аккаунтов.\n\n"
        "Доступные команды:\n"
        "/add - добавить аккаунт (буду задавать вопросы)\n"
        "/list - показать сохранённые аккаунты\n"
        "/compare <u1> <u2> ... - сравнить несколько аккаунтов (если без аргументов — возьму все)\n"
        "/export - сохранить данные в CSV\n"
        "/clear - очистить данные чата\n"
        "/formulas - показать формулы расчёта метрик\n"
        "/help - помощь\n\n"
        "Важно: вы сами вводите данные (подписчики, лайки, комментарии)."
    )
    await update.message.reply_text(txt)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ========== Add flow ==========
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добавление аккаунта. Введите username (ник без @):")
    return A_USERNAME

async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lstrip("@")
    context.user_data['new_account'] = {"username": username}
    await update.message.reply_text(f"Username: @{username}\nСколько у него подписчиков? (целое число)")
    return A_FOLLOWERS

async def add_followers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = int(update.message.text.strip())
        context.user_data['new_account']['followers'] = v
    except Exception:
        await update.message.reply_text("Нужно целое число. Повторите ввод подписчиков:")
        return A_FOLLOWERS
    await update.message.reply_text("Среднее число лайков на пост? (например 72)")
    return A_AVG_LIKES

async def add_avg_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        context.user_data['new_account']['avg_likes'] = v
    except Exception:
        await update.message.reply_text("Нужно число. Введите средние лайки:")
        return A_AVG_LIKES
    await update.message.reply_text("Среднее число комментариев на пост? (например 5)")
    return A_AVG_COMMENTS

async def add_avg_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        context.user_data['new_account']['avg_comments'] = v
    except Exception:
        await update.message.reply_text("Нужно число. Введите средние комменты:")
        return A_AVG_COMMENTS
    await update.message.reply_text("Сколько постов в неделю в среднем? (например 2)")
    return A_POSTS_PER_WEEK

async def add_posts_per_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        context.user_data['new_account']['posts_per_week'] = v
    except Exception:
        await update.message.reply_text("Нужно число. Введите посты в неделю:")
        return A_POSTS_PER_WEEK
    await update.message.reply_text("Сколько недель из последних N аккаунт был активен?")
    return A_WEEKS_ACTIVE

async def add_weeks_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        context.user_data['new_account']['weeks_active'] = v
    except Exception:
        await update.message.reply_text("Нужно число. Введите количество недель с активностью:")
        return A_WEEKS_ACTIVE
    await update.message.reply_text("Общее число недель для расчёта (например 12):")
    return A_TOTAL_WEEKS

async def add_total_weeks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        context.user_data['new_account']['total_weeks'] = v
    except Exception:
        await update.message.reply_text("Нужно число. Введите общее число недель:")
        return A_TOTAL_WEEKS
    await update.message.reply_text("Использует ли аккаунт Stories? (да/нет)")
    return A_STORIES

async def add_stories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().lower()
    val = txt in ("да", "yes", "y", "true", "1")
    context.user_data['new_account']['uses_stories'] = val
    await update.message.reply_text("Оцени визуальный стиль 1..5 (1 — плохо, 5 — отлично):")
    return A_VISUAL_STYLE

async def add_visual_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        if v < 1 or v > 5:
            raise ValueError()
        context.user_data['new_account']['visual_style'] = v
    except Exception:
        await update.message.reply_text("Введи число от 1 до 5:")
        return A_VISUAL_STYLE
    await update.message.reply_text("Укажи индекс взаимной активности (IA) в процентах (0-100). Если не знаешь — введи 0:")
    return A_IA_PERCENT

async def add_ia_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        v = float(update.message.text.strip())
        if v < 0:
            raise ValueError()
        context.user_data['new_account']['ia_percent'] = v
    except Exception:
        await update.message.reply_text("Нужно число >= 0. Введи IA в процентах:")
        return A_IA_PERCENT

    # Сохраняем аккаунт
    acc = context.user_data.pop('new_account')
    chat_id = update.effective_chat.id
    data = load_chat_data(chat_id)
    uname = acc['username']

    er = compute_ER(acc.get('followers', 0), acc.get('avg_likes', 0.0), acc.get('avg_comments', 0.0))
    is_ = compute_IS(acc.get('weeks_active', 0.0), acc.get('total_weeks', 0.0))
    vs_pct = normalize_VS(acc.get('visual_style', 0.0))
    ia = acc.get('ia_percent', 0.0)

    acc['ER'] = er
    acc['IS'] = is_
    acc['VS_pct'] = vs_pct
    acc['IA'] = ia
    acc['I'] = compute_I(er, is_, ia, vs_pct)

    data['accounts'][uname] = acc
    if uname not in data['order']:
        data['order'].append(uname)
    save_chat_data(chat_id, data)

    await update.message.reply_text(f"✅ Сохранено: @{uname}\nХочешь добавить ещё аккаунт? (да/нет)")
    return A_MORE_ACCOUNTS

async def add_more_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().lower()
    if txt in ("да", "yes", "y"):
        await update.message.reply_text("Введите следующий username (без @):")
        return A_USERNAME
    else:
        await update.message.reply_text("Все аккаунты добавлены. Можешь использовать /compare для анализа.")
        return ConversationHandler.END

async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('new_account', None)
    await update.message.reply_text("Добавление отменено.")
    return ConversationHandler.END

# ========== Прочие команды ==========
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_chat_data(update.effective_chat.id)
    if not data['order']:
        await update.message.reply_text("Нет сохранённых аккаунтов. Добавь с помощью /add")
        return
    lines = ["Сохранённые аккаунты:"]
    for uname in data['order']:
        acc = data['accounts'].get(uname, {})
        lines.append(f"@{uname} — I={acc.get('I', 0):.3f}" if acc.get('I') else f"@{uname} — I:N/A")
    await update.message.reply_text("\n".join(lines))

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_chat_data(chat_id, {"accounts": {}, "order": []})
    await update.message.reply_text("Данные очищены.")

async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import csv
    chat_id = update.effective_chat.id
    data = load_chat_data(chat_id)
    if not data['order']:
        await update.message.reply_text("Нет данных для экспорта.")
        return
    out_path = os.path.join(DATA_DIR, f"export_{chat_id}.csv")
    keys = ["username","followers","avg_likes","avg_comments","posts_per_week","weeks_active","total_weeks","uses_stories","visual_style","ia_percent","ER","IS","IA","VS_pct","I"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(keys)
        for u in data['order']:
            acc = data['accounts'].get(u, {})
            row = [acc.get(k) for k in keys]
            writer.writerow(row)
    await update.message.reply_document(open(out_path, "rb"))

# ========== Compare ==========
async def compare_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    data = load_chat_data(update.effective_chat.id)
    if not data['order']:
        await update.message.reply_text("Нет аккаунтов для сравнения.")
        return

    to_compare = [a.lstrip("@") for a in args] if args else data['order']
    found = []
    not_found = []
    for u in to_compare:
        if u in data['accounts']:
            found.append(data['accounts'][u])
        else:
            not_found.append(u)
    if not_found:
        await update.message.reply_text("Не найдены данные по: " + ", ".join(not_found))
        return

    # Сортировка по I
    sorted_accs = sorted(found, key=lambda x: x.get('I') or 0, reverse=True)

    # Лидеры по каждой метрике
    best_ER = max(found, key=lambda x: x.get('ER') or 0)
    best_IS = max(found, key=lambda x: x.get('IS') or 0)
    best_IA = max(found, key=lambda x: x.get('IA') or 0)
    best_VS = max(found, key=lambda x: x.get('VS_pct') or 0)
    best_I = sorted_accs[0]

    lines = ["📊 Сравнение аккаунтов:"]
    for i, acc in enumerate(sorted_accs, start=1):
        er = f"{acc['ER']:.2f}%" if acc['ER'] is not None else "N/A"
        is_ = f"{acc['IS']:.2f}%" if acc['IS'] is not None else "N/A"
        ia = f"{acc['IA']:.2f}%"
        vs = f"{acc['visual_style']} ({acc['VS_pct']:.1f}%)"
        lines.append(f"{i}. @{acc['username']} — I={acc['I']:.3f}\n   ER={er}, IS={is_}, IA={ia}, VS={vs}")

    await update.message.reply_text("\n\n".join(lines))

    explanation = (
        f"\n🏆 Лидер по общей оценке I: @{best_I['username']} — {best_I['I']:.3f}\n"
        f"ER — вовлечённость: @{best_ER['username']} ({best_ER['ER']:.2f}%) — показывает активность аудитории.\n"
        f"IS — активность аккаунта: @{best_IS['username']} ({best_IS['IS']:.2f}%) — показывает стабильность активности.\n"
        f"IA — взаимная активность: @{best_IA['username']} ({best_IA['IA']:.2f}%) — качество взаимодействия с подписчиками.\n"
        f"VS — визуальный стиль: @{best_VS['username']} ({best_VS['VS_pct']:.1f}%) — привлекательность контента.\n"
    )
    await update.message.reply_text(explanation)

# ========== Formulas ==========
async def formulas_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "📐 Формулы расчёта метрик:\n\n"
        "1️⃣ ER (вовлечённость):\n"
        "   ER = (avg_likes + avg_comments) / followers * 100%\n\n"
        "2️⃣ IS (активность аккаунта):\n"
        "   IS = weeks_active / total_weeks * 100%\n\n"
        "3️⃣ VS (визуальный стиль):\n"
        "   VS_pct = VS_rating / 5 * 100%\n\n"
        "4️⃣ I (индекс влияния):\n"
        "   I = 0.4*ER + 0.3*IS + 0.2*IA + 0.1*VS_pct\n"
    )
    await update.message.reply_text(txt)

# ========== Error handler ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("Error:", context.error)

# ========== Setup handlers ==========
def add_handlers(application):
    """Add all handlers to the application"""
    conv = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            A_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_username)],
            A_FOLLOWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_followers)],
            A_AVG_LIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_avg_likes)],
            A_AVG_COMMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_avg_comments)],
            A_POSTS_PER_WEEK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_posts_per_week)],
            A_WEEKS_ACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_weeks_active)],
            A_TOTAL_WEEKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_total_weeks)],
            A_STORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stories)],
            A_VISUAL_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_visual_style)],
            A_IA_PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_ia_percent)],
            A_MORE_ACCOUNTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_more_accounts)],
        },
        fallbacks=[CommandHandler('cancel', add_cancel)],
        allow_reentry=True
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(conv)
    application.add_handler(CommandHandler("list", list_cmd))
    application.add_handler(CommandHandler("clear", clear_cmd))
    application.add_handler(CommandHandler("export", export_cmd))
    application.add_handler(CommandHandler("compare", compare_cmd))
    application.add_handler(CommandHandler("formulas", formulas_cmd))
    application.add_error_handler(error_handler)

# ========== Polling mode (local development) ==========
def main():
    """Main function - runs in polling mode"""
    import asyncio
    
    async def run_polling():
        if not TOKEN:
            print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
            print("Please set your Telegram bot token using the Secrets feature.")
            return
        
        application = ApplicationBuilder().token(TOKEN).build()
        add_handlers(application)
        
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("Bot is running in POLLING mode (local development)...")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\nStopping bot...")
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
    
    asyncio.run(run_polling())

# ========== Webhook mode (for Render) ==========
async def run_webhook():
    """Run in webhook mode for deployment"""
    import asyncio
    from aiohttp import web
    
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
        return
    
    PORT = int(os.getenv("PORT", 8000))
    WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")
    
    if not WEBHOOK_URL:
        print("❌ Error: RENDER_EXTERNAL_URL not set. Webhook mode requires deployment URL.")
        return
    
    application = ApplicationBuilder().token(TOKEN).updater(None).build()
    add_handlers(application)
    
    await application.initialize()
    await application.start()
    
    async def webhook_handler(request):
        """Handle incoming webhook updates from Telegram"""
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.update_queue.put(update)
            return web.Response(text="OK")
        except Exception as e:
            print(f"Webhook error: {e}")
            return web.Response(status=500)
    
    async def health_check(request):
        """Health check endpoint for Render"""
        return web.Response(text="OK")
    
    async def on_startup(app_web):
        """Set webhook on startup"""
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await application.bot.set_webhook(webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")
        print(f"Bot is running in WEBHOOK mode on port {PORT}...")
    
    async def on_shutdown(app_web):
        """Cleanup on shutdown"""
        await application.bot.delete_webhook()
        await application.stop()
        await application.shutdown()
    
    web_app = web.Application()
    web_app.router.add_post('/webhook', webhook_handler)
    web_app.router.add_get('/health', health_check)
    web_app.on_startup.append(on_startup)
    web_app.on_shutdown.append(on_shutdown)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    MODE = os.getenv("BOT_MODE", "polling")
    
    if MODE == "webhook":
        import asyncio
        asyncio.run(run_webhook())
    else:
        main()
