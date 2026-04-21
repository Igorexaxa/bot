# 🚀 Telegram Bot for Amnezia VPN Panel

Автоматизированный Telegram-бот для продажи подписок и управления VPN-ключами. Полная интеграция с API [Amnezia VPN Panel](https://github.com/infosave2007/amneziavpnphp).

## ✨ Основные возможности

*   **🛒 Продажа подписок**: Автоматический прием оплаты через Telegram Invoices (Stars, Банковские карты).
*   **🔑 Динамическое управление**: Бот автоматически подтягивает серверы и протоколы (AmneziaWG, XRay VLESS, Shadowsocks и др.) из вашей панели.
*   **🌍 Авто-локация**: Автоматическое определение страны сервера по IP и добавление соответствующего флага в меню.
*   **📊 Статистика трафика**: Отображение объема скачанных и загруженных данных для каждого ключа.
*   **📅 Менеджер подписок**: Автоматическое удаление ключей с сервера по истечении срока действия подписки.
*   **🛠 Админ-панель**: Статистика, выдача подписок по ID и создание бэкапов базы данных одной командой.

## 📋 Требования

*   Python 3.10+
*   Установленная панель [amneziavpnphp](https://github.com)
*   Docker (для работы функции бэкапа базы данных)

## 🛠 Установка

1. **Клонируйте репозиторий:**
   
   ```bash
   git clone https://github.com/Igorexaxa/bot
   cd ваш-репозиторий
  
Создайте и активируйте виртуальное окружение:

python3 -m venv venv
source venv/bin/activate


Установите зависимости:

pip install aiogram requests

Настройте переменные окружения:
Отредактируйте переменные в начале файла bot.py или создайте .env файл:
BOT_TOKEN: Токен от @BotFather.
API_URL: URL вашей панели (например, https://example.com).
ADMIN_ID: Ваш цифровой ID в Telegram.
🚀 Запуск через Systemd (Автозапуск)
Для обеспечения работы бота 24/7 создайте службу:
Откройте редактор:
🚀 Запуск через Systemd (Автозапуск)
Для обеспечения работы бота 24/7 создайте службу:

Откройте редактор:

sudo nano /etc/systemd/system/vpn-bot.service

Вставьте конфигурацию (измените пути на свои):

[Unit]
Description=Telegram Amnezia VPN Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/your/bot
ExecStart=/path/to/your/bot/venv/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

Примените и запустите:

sudo systemctl daemon-reload
sudo systemctl enable vpn-bot
sudo systemctl start vpn-bot

📂 Структура базы данных
Бот использует SQLite (users.db) для хранения данных о пользователях и сроках их подписки. Файл создается автоматически при первом запуске.

🛡 Безопасность
Никогда не публикуйте свой users.db и файл с токенами в открытый доступ.
Используйте .gitignore, чтобы исключить секретные файлы из репозитория.

🤝 Обратная связь
Если вы нашли ошибку или хотите предложить улучшение, создайте Issue или Pull Request.
Powered by [Amnezia VPN Panel](https://github.com/infosave2007/amneziavpnphp)
