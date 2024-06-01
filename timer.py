import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime, timedelta

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для хранения напоминаний
reminders = {}

# Обработка команды /remind
def remind(update: Update, context: CallbackContext) -> None:
    try:
        # Разбор аргументов команды
        args = context.args
        remind_time = datetime.strptime(args[0], '%Y-%m-%d %H:%M')
        reminder_text = ' '.join(args[1:])

        # Получение chat_id пользователя
        chat_id = update.message.chat_id

        # Добавление напоминания в словарь
        if chat_id not in reminders:
            reminders[chat_id] = []
        reminders[chat_id].append({'time': remind_time, 'text': reminder_text})

        update.message.reply_text(f'Напоминание установлено на {remind_time.strftime("%Y-%m-%d %H:%M")}')
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /remind YYYY-MM-DD HH:MM ваше_напоминание')

# Функция для отправки напоминаний
def send_reminders(context: CallbackContext) -> None:
    now = datetime.now()
    for chat_id, reminder_list in reminders.items():
        for reminder in reminder_list:
            if reminder['time'] <= now:
                context.bot.send_message(chat_id=chat_id, text=f'Напоминание: {reminder["text"]}')
                reminder_list.remove(reminder)

def main() -> None:
    # Инициализация бота
    updater = Updater(token=os.environ.get('6562877457:AAECx1_cu0_KBVJCMrQ7aDX0U0XOV0O__1s'), use_context=True)
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler("remind", remind))

    # Запуск регулярной отправки напоминаний
    job_queue = updater.job_queue
    job_queue.run_repeating(send_reminders, interval=60, first=0)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
