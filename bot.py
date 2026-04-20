import asyncio, requests, base64, logging, time, sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ ---
BOT_TOKEN = ""
ADMIN_ID = ID_Telegram 
ADMIN_PASSWORD = "pass"
API_URL = "https://сайт/api"
ADMIN_EMAIL = "admin@amnez.ia"
PROXY_URL = "socks5://адрес_порт"
PAYMENT_TOKEN = ""
PRICE_AMOUNT = 100 
# -----------------

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_flag(ip):
    try:
        # Получаем код страны по IP (бесплатное API)
        response = requests.get(f"http://ip-api.com{ip}", timeout=5).json()
        country_code = response.get('countryCode', 'UN') # UN если не найдено
        # Конвертируем код страны (RU, US) в эмодзи-флаг
        return "".join(chr(ord(c) + 127397) for c in country_code.upper())
    except:
        return "🌐"

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
        r = requests.post(f"{API_URL}/auth/token", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=10)
        return r.json().get("token")
    except: return None

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    exp = get_expiry(message.from_user.id)
    status = f"✅ До: {exp.strftime('%d.%m.%Y')}" if exp and exp > datetime.now() else "❌ Не активна"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Создать ключ", callback_data="menu_servers")],
        [InlineKeyboardButton(text="🗂 Мои ключи", callback_data="menu_list")],
        [InlineKeyboardButton(text="💳 Продлить подписку", callback_data="buy_sub")]
    ])
    await message.answer(f"🛒 **Меню VPN**\n\nСтатус: {status}", reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await message.answer("Выберите действие:", reply_markup=kb)

@dp.callback_query(F.data == "menu_servers")
async def show_servers(callback: types.CallbackQuery):
    exp = get_expiry(callback.from_user.id)
    if not exp or exp < datetime.now(): return await callback.answer("⚠️ Требуется подписка!", show_alert=True)
    
    await callback.message.edit_text("⏳ Определяю локации серверов...")
    token = get_token()
    r = requests.get(f"{API_URL}/servers", headers={"Authorization": f"Bearer {token}"})
    servers = r.json().get("servers", [])
    
    buttons = []
    for s in servers:
        flag = get_flag(s['ip'])
        buttons.append([InlineKeyboardButton(text=f"{flag} {s['name']}", callback_data=f"srv_{s['id']}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")])
    await callback.message.edit_text("Выберите сервер:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("srv_"))
async def show_protocols(callback: types.CallbackQuery):
    server_id = callback.data.split("_")[1]
    token = get_token()
    r = requests.get(f"{API_URL}/protocols/active", headers={"Authorization": f"Bearer {token}"})
    protocols = r.json().get("protocols", [])
    
    buttons = [[InlineKeyboardButton(text=f"🛡 {p['name']}", callback_data=f"create_{server_id}_{p['id']}")] for p in protocols]
    buttons.append([InlineKeyboardButton(text="⬅️ К серверам", callback_data="menu_servers")])
    await callback.message.edit_text("Выберите протокол:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("create_"))
async def create_vpn(callback: types.CallbackQuery):
    _, s_id, p_id = callback.data.split("_")
    await callback.message.edit_text("⏳ Генерирую ключ...")
    token = get_token()
    client_name = f"user_{callback.from_user.id}_{int(time.time())}"
    r = requests.post(f"{API_URL}/clients/create", 
                      json={"server_id": int(s_id), "name": client_name, "protocol_id": int(p_id)}, 
                      headers={"Authorization": f"Bearer {token}"}, timeout=65)
    res = r.json()
    if res.get("success"):
        c = res["client"]
        qr_bytes = base64.b64decode(c["qr_code"].split(",")[-1])
        await callback.message.answer_photo(BufferedInputFile(qr_bytes, filename="qr.png"), 
                                           caption=f"✅ Готово!\n\n`{c['config']}`", parse_mode="Markdown")
    else: await callback.message.answer(f"Ошибка: {res.get('message')}")

@dp.callback_query(F.data == "menu_list")
async def list_keys(callback: types.CallbackQuery):
    token = get_token()
    r = requests.get(f"{API_URL}/servers", headers={"Authorization": f"Bearer {token}"})
    servers = r.json().get("servers", [])
    u_id = str(callback.from_user.id)
    buttons = []
    for s in servers:
        rc = requests.get(f"{API_URL}/servers/{s['id']}/clients", headers={"Authorization": f"Bearer {token}"})
        flag = get_flag(s['ip'])
        for c in rc.json().get("clients", []):
            if u_id in str(c['name']):
                buttons.append([InlineKeyboardButton(text=f"🔑 {flag} {s['name']} | ID:{c['id']}", callback_data=f"getkey_{c['id']}")])
    
    if not buttons: return await callback.answer("Ключей нет")
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")])
    await callback.message.edit_text("Ваши ключи:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("getkey_"))
async def get_key_data(callback: types.CallbackQuery):
    c_id = callback.data.split("_")[1]; token = get_token()
    r = requests.get(f"{API_URL}/clients/{c_id}/details", headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 200:
        c = r.json().get("client")
        qr_bytes = base64.b64decode(c["qr_code"].split(",")[-1])
        await callback.message.answer_photo(BufferedInputFile(qr_bytes, filename="qr.png"), caption=f"Ключ: {c['name']}")
        await callback.message.answer(f"```\n{c['config']}\n```", parse_mode="Markdown")

@dp.callback_query(F.data == "menu_back")
async def back(c: types.CallbackQuery): await cmd_start(c.message)

@dp.callback_query(F.data == "buy_sub")
async def pay(c: types.CallbackQuery):
    await c.message.answer_invoice(title="Подписка", description="30 дней", payload="sub", 
                                   provider_token=PAYMENT_TOKEN, currency="RUB", 
                                   prices=[LabeledPrice(label="30 дней", amount=PRICE_AMOUNT*100)])

@dp.pre_checkout_query()
async def checkout(q: types.PreCheckoutQuery): await q.answer(ok=True)

@dp.message(F.successful_payment)
async def success_pay(m: types.Message):
    add_subscription(m.from_user.id)
    await m.answer("✅ Подписка активирована!")

async def main():
    init_db(); session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=BOT_TOKEN, session=session)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
