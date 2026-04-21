# 🚀 Telegram VPN Manager for Amnezia VPN

Автоматизированная система управления VPN-подписками через Telegram. Проект обеспечивает интеграцию с API панели [amneziavpnphp](https://github.com/infosave2007/amneziavpnphp), позволяя пользователям самостоятельно управлять своими ключами.

---

## ✨ Ключевые возможности

### 👤 Для пользователей
* **💳 Оплата и подписка**: Интеграция с Telegram Invoices для автоматической продажи доступа (30 дней).
* **🌍 Глобальная сеть**: Динамический выбор серверов с автоматическим определением флагов стран и пинга.
* **🛡 Безопасность**: Поддержка протоколов AmneziaWG 2.0, XRay VLESS и других.
* **📱 Удобство**: Получение QR-кодов и текстовых конфигураций прямо в чате.
* **📊 Прозрачность**: Отображение реального расхода трафика (Upload/Download) по каждому ключу.

### 👑 Для владельца (Админ-панель)
* **🔧 Полная автоматизация**: Бот сам удаляет ключи с сервера, когда у пользователя истекает подписка.
* **📦 Бэкап в один клик**: Команда `/backup` присылает дампы баз данных панели и бота в личные сообщения.
* **🎟 Гибкое управление**: Возможность ручной выдачи или продления подписки по ID пользователя.
* **🆘 Техподдержка**: Система обратной связи с пользователями через Reply-сообщения.

---

## 📋 Требования к среде

- **Python** 3.10+
- **Amnezia VPN Panel** [установленная на сервере](https://github.com/infosave2007/amneziavpnphp))
- **Docker** (для работы функции резервного копирования базы данных панели)
- **SQLite3** (для локального хранения данных о подписках)

---

## 🛠 Быстрый старт

1. **Клонирование и установка зависимостей**:
   ```bash
   git clone https://github.com/Igorexaxa/bot
   cd ВАШ_РЕПОЗИТОРИЙ
   python3 -m venv venv
   source venv/bin/activate
   pip install aiogram requests

2.Настройка конфигурации:
   
Укажите в коде или через переменные окружения:
``bash
BOT_TOKEN (от @BotFather)
ADMIN_ID (ваш ID)
API_URL (URL вашей панели)
Запуск службы (Systemd):
Создайте файл /etc/systemd/system/vpn-bot.service для обеспечения бесперебойной работы и автозапуска после перезагрузки сервера.

3. Настройка автозапуска (Systemd)
Чтобы бот работал 24/7, создайте службу:

```bash
sudo nano /etc/systemd/system/vpn-bot.service
```
Вставьте конфигурацию
```
[Unit]
Description=Telegram Amnezia VPN Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/venv/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Developed for use with Amnezia [VPN Panel API](https://github.com/infosave2007/amneziavpnphp)
```
