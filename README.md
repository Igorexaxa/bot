# Amnezia VPN Telegram Bot 🚀

Телеграм-бот для автоматизации продажи и управления VPN-ключами на базе **Amnezia VPN Panel**.

## Основные возможности
- 🛡 **Динамические протоколы**: Поддержка AmneziaWG, XRay (VLESS), Shadowsocks и др.
- 🌍 **Мультисерверность**: Выбор локаций прямо в боте.
- 💳 **Платежи**: Прием оплаты подписки (30 дней) через Telegram Invoices.
- 🔑 **Личный кабинет**: Просмотр ранее созданных ключей и конфигураций.
- 📅 **Система подписок**: Контроль срока доступа через SQLite.
- 🗄 **Админ-панель**: Выдача подписок по ID и создание бэкапов БД одной командой.

## Требования
- Python 3.10+
- Развернутая [Amnezia VPN Panel](https://github.com)
- Docker (для работы функции бэкапа)

## Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com
cd amnezia-vpn-bot

Создайте виртуальное окружение и установите зависимости:
bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Настройте переменные окружения в файле .env или системно.
Переменные окружения (Environment Variables)
Переменная	Описание
BOT_TOKEN	Токен от @BotFather
ADMIN_ID	Ваш цифровой Telegram ID
API_URL	URL вашей Amnezia Panel API (с /api)
ADMIN_PASSWORD	Пароль администратора панели
PAYMENT_TOKEN	Токен платежного провайдера (для инвойсов)

Запуск

python bot.py


## Настройка автозапуска (Systemd)

Чтобы бот работал 24/7 и автоматически запускался после перезагрузки сервера, создайте системную службу:

1. Создайте файл службы:
```bash
sudo nano /etc/systemd/system/vpn-bot.service

Вставьте следующее содержимое (отредактируйте пути /www/tg_bot на свои):

[Unit]
Description=Telegram Amnezia VPN Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/www/tg_bot
ExecStart=/www/tg_bot/venv/bin/python3 /www/tg_bot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

Активируйте и запустите бота:
bash
sudo systemctl daemon-reload
sudo systemctl enable vpn-bot
sudo systemctl start vpn-bot
Используйте код с осторожностью.
Проверка статуса и логов:
bash
sudo systemctl status vpn-bot



