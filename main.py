from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from process_message import process_message, top_scores, set_custom_message
from reset_scores import reset_scores
#from inactivity_bot import send_reminder

YOUR_BOT_TOKEN = "6728046696:AAEO8ZI0G8AHLhzj22DbBJVFKz2UY2Na7aU"
allowed_user_id = 1391595972

def main():
    updater = Updater(YOUR_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("reseta", reset_scores))
    dispatcher.add_handler(CommandHandler("top", top_scores))
    dispatcher.add_handler(CommandHandler("set", set_custom_message))  # Добавляем обработчик для команды /set

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    updater.start_polling()

    # Добавляем функцию send_reminder для проверки неактивности
    #job_queue = updater.job_queue
    #dispatcher.add_handler(MessageHandler(Filters.all, lambda update, context: job_queue.run_once(send_reminder, 10, context=update.message.chat_id)))

    updater.idle()
    
if __name__ == '__main__':
    main()
