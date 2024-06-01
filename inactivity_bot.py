from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, timedelta

# Функция для отправки сообщения, если пользователь долго не пишет
def send_reminder(context):
    job = context.job
    last_active_time = job.context['last_active_time']
    current_time = datetime.now()
    time_difference = current_time - last_active_time

    # Проверяем, прошло ли более 10 секунд с последнего сообщения пользователя
    if time_difference.total_seconds() >= 10:
        context.bot.send_message(job.context['chat_id'], text="Вы долго молчали! Напишите что-нибудь.")

# Обработчик для текстовых сообщений
def text_message(update, context):
    # Получаем объект пользователя
    user = update.message.from_user

    # Обновляем время последнего активного сообщения от пользователя
    context.job_queue.run_once(send_reminder, 10, context={'last_active_time': datetime.now(), 'chat_id': update.message.chat_id})


# Инициализация бота и добавление обработчика сообщений
updater = Updater("YOUR_TOKEN", use_context=True)
dispatcher = updater.dispatcher

text_message_handler = MessageHandler(Filters.text & (~Filters.command), text_message)
dispatcher.add_handler(text_message_handler)

# Запуск бота
updater.start_polling()
updater.idle()
