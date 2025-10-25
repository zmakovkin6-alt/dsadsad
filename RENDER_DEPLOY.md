# Как развернуть бота на Render (бесплатно!)

## Шаг 1: Подготовка GitHub репозитория

1. **Создайте аккаунт на GitHub** (если ещё нет): https://github.com
2. **Создайте новый репозиторий:**
   - Нажмите "New repository" (зелёная кнопка)
   - Назовите его (например: `telegram-influence-bot`)
   - Сделайте его **Public** (публичным)
   - Нажмите "Create repository"

3. **Загрузите код:**
   
   В Replit нажмите на иконку **Source Control** (ветка) в левой панели, или используйте терминал:
   
   ```bash
   git remote add origin https://github.com/ВАШ_USERNAME/telegram-influence-bot.git
   git add .
   git commit -m "Initial commit - Telegram bot ready for Render"
   git push -u origin main
   ```
   
   Если попросит логин/пароль - используйте Personal Access Token вместо пароля.

## Шаг 2: Регистрация на Render

1. Перейдите на https://render.com
2. Нажмите **"Get Started"**
3. Зарегистрируйтесь через **GitHub** (проще всего)
4. Разрешите Render доступ к вашим репозиториям

## Шаг 3: Создание Web Service

1. На главной странице Render нажмите **"New +"** → **"Web Service"**

2. Подключите ваш GitHub репозиторий:
   - Найдите `telegram-influence-bot` в списке
   - Нажмите **"Connect"**

3. **Настройте сервис:**
   
   - **Name**: `telegram-influence-bot` (или любое имя)
   - **Region**: выберите ближайший (Europe/Frankfurt)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python influence_bot.py`
   
4. **Выберите план:**
   - Выберите **"Free"** (бесплатный план)

5. **Добавьте Environment Variables (переменные окружения):**
   
   Нажмите **"Advanced"** → **"Add Environment Variable"**
   
   Добавьте ДВЕ переменные:
   
   ```
   Key: TELEGRAM_BOT_TOKEN
   Value: ВАШ_ТОКЕН_ОТ_BOTFATHER
   
   Key: BOT_MODE
   Value: webhook
   ```
   
   ⚠️ **Важно**: Токен вставляйте БЕЗ кавычек!

6. **Нажмите "Create Web Service"**

## Шаг 4: Дождитесь деплоя

- Render начнёт установку зависимостей и запуск бота
- Это займёт 2-3 минуты
- Следите за логами (они будут показываться на экране)
- Когда увидите "✅ Webhook set to..." - всё готово!

## Шаг 5: Проверка работы

1. **Найдите URL вашего сервиса:**
   - Вверху страницы будет что-то вроде: `https://telegram-influence-bot-xxxx.onrender.com`

2. **Проверьте health endpoint:**
   - Откройте в браузере: `https://ВАШ-URL.onrender.com/health`
   - Должно показать "OK"

3. **Проверьте бота в Telegram:**
   - Найдите вашего бота
   - Отправьте `/start`
   - Бот должен ответить! 🎉

## Важная информация о бесплатном плане

✅ **Плюсы:**
- Совершенно бесплатно
- 750 часов в месяц (хватит на целый месяц 24/7)
- Автоматические перезапуски при сбоях

⚠️ **Минусы:**
- Бот "засыпает" через 15 минут без активности
- Первое сообщение после сна может занять 30-60 секунд
- Потом работает нормально

## Как предотвратить засыпание (опционально)

Можно использовать сервис **UptimeRobot** для автопинга:

1. Зарегистрируйтесь на https://uptimerobot.com (бесплатно)
2. Создайте новый монитор:
   - Type: HTTP(s)
   - URL: `https://ВАШ-URL.onrender.com/health`
   - Monitoring Interval: 5 minutes
3. Сохраните

Теперь бот будет "просыпаться" каждые 5 минут и не заснёт!

## Обновление бота

Когда захотите обновить код:

1. Измените код в Replit
2. Закоммитьте и запушьте в GitHub:
   ```bash
   git add .
   git commit -m "Update bot"
   git push
   ```
3. Render автоматически заметит изменения и передеплоит бота

## Логи и отладка

- **Смотреть логи:** На странице сервиса в Render → вкладка "Logs"
- **Перезапустить:** Кнопка "Manual Deploy" → "Clear build cache & deploy"

## Помощь

Если что-то не работает:

1. Проверьте логи в Render
2. Убедитесь, что `BOT_MODE=webhook` установлен
3. Проверьте что токен правильный
4. Посмотрите webhook status:
   ```
   https://api.telegram.org/botВАШ_ТОКЕН/getWebhookInfo
   ```

Удачи! 🚀
