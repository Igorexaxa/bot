import asyncio, requests, base64, logging, time, sqlite3, os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ (Данные берутся из переменных окружения сервера) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ПАРОЛЬ_ПАНЕЛИ")
API_URL = os.getenv("API_URL", "https://your-panel.ru")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@email.com")
PROXY_URL = os.getenv("PROXY_URL") # Необязательно

# ПЛАТЕЖИ
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
PRICE_AMOUNT = int(os.getenv("PRICE_AMOUNT", 100))
CURRENCY = os.getenv("CURRENCY", "RUB")

# Названия серверов
CUSTOM_NAMES = {"1": "Server #1", "2": "Server #2"}
# ---------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, expiry_date TEXT)')
    conn.commit(); conn.close()

def get_expiry(user_id):
    conn = sqlite3.connect('users.db'); cur = conn.cursor()
    cur.execute("SELECT expiry_date FROM users WHERE user_id = ?", (str(user_id),))
    res = cur.fetchone(); conn.close()
    return datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S') if res else None

def add_subscription(user_id, days=30):
    current = get_expiry(user_id) or datetime.now()
    if current < datetime.now(): current = datetime.now()
    new_date = current + timedelta(days=days)
    conn = sqlite3.connect('users.db'); cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (str(user_id), new_date.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit(); conn.close()
    return new_date

def get_token():
    try:
        r = requests.post(f"{API_URL}/auth/token", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
        return r.json().get("token")
    except: return None

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect('users.db'); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users"); total = cur.fetchone()[0]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("SELECT COUNT(*) FROM users WHERE expiry_date > ?", (now,))
    active = cur.fetchone()[0]; conn.close()
    await message.answer(f"📈 **Админка**\nЮзеров: {total}\nАктивных: {active}\n\n`/backup` - бэкап\n`/give ID ДНИ`")

@dp.message(Command("backup"))
async def cmd_backup(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("🔄 Создаю бэкап...")
    db_path = "users.db"
    dump_file = "amnezia_dump.sql"
    if os.path.exists(db_path):
        await message.answer_document(FSInputFile(db_path), caption="База бота")
    os.system(f"docker exec amnezia-panel-db mysqldump -u amnezia -pamnezia amnezia > {dump_file}")
    if os.path.exists(dump_file) and os.path.getsize(dump_file) > 0:
        await message.answer_document(FSInputFile(dump_file), caption="Дамп Amnezia")
        os.remove(dump_file)

@dp.message(Command("start"))
@dp.message(F.text == "🚀 Получить VPN-ключ")
async def cmd_start(message: types.Message):
    exp = get_expiry(message.from_user.id)
    status = f"✅ До: {exp.strftime('%d.%m.%Y')}" if exp and exp > datetime.now() else "❌ Не активна"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Создать ключ", callback_data="menu_servers")],
        [InlineKeyboardButton(text="🗂 Мои ключи", callback_data="menu_list")],
        [InlineKeyboardButton(text="💳 Продлить подписку", callback_data="buy_sub")]
    ])
    await message.answer(f"🛒 **Меню VPN**\nСтатус: {status}", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите действие:", reply_markup=kb)

@dp.callback_query(F.data == "buy_sub")
async def pay_invoice(c: types.CallbackQuery):
    if not PAYMENT_TOKEN: return await c.answer("Платежи не настроены", show_alert=True)
    await c.message.answer_invoice(
        title="VPN Подписка", description="Доступ на 30 дней", payload="sub",
        provider_token=PAYMENT_TOKEN, currency=CURRENCY, 
        prices=[LabeledPrice(label="30 дней", amount=PRICE_AMOUNT * 100)]
    )

@dp.pre_checkout_query()
async def checkout(q: PreCheckoutQuery): await q.answer(ok=True)

@dp.message(F.successful_payment)
async def success_pay(m: types.Message):
    add_subscription(m.from_user.id)
    await m.answer("✅ Оплата прошла! Подписка активна.")

@dp.callback_query(F.data == "menu_servers")
async def show_servers(callback: types.CallbackQuery):
    exp = get_expiry(callback.from_user.id)
    if not exp or exp < datetime.now(): return await callback.answer("⚠️ Требуется подписка!", show_alert=True)
    token = get_token()
    r = requests.get(f"{API_URL}/servers", headers={"Authorization": f"Bearer {token}"})
    servers = r.json().get("servers", [])
    btns = [[InlineKeyboardButton(text=f"🌍 {CUSTOM_NAMES.get(str(s['id']), s['name'])}", callback_data=f"srv_{s['id']}")] for s in servers]
    btns.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")])
    await callback.message.edit_text("Выберите сервер:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@dp.callback_query(F.data.startswith("srv_"))
async def show_proto(c: types.CallbackQuery):
    s_id = c.data.split("_")[1]; token = get_token()
    r = requests.get(f"{API_URL}/protocols/active", headers={"Authorization": f"Bearer {token}"})
    protocols = r.json().get("protocols", [])
    btns = [[InlineKeyboardButton(text=f"🛡 {p['name']}", callback_data=f"create_{s_id}_{p['id']}")] for p in protocols]
    await c.message.edit_text("Протокол:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

async def main():
    init_db()
    session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
    bot = Bot(token=BOT_TOKEN, session=session)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
