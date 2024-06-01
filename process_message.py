import os
import json
import re
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Bot
from telegram.error import BadRequest, Unauthorized
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

allowed_user_id = 1391595972

def process_message(update: Update, context: CallbackContext) -> None:
    allowed_chat_id = -1002140769164
    if update.effective_chat.id != allowed_chat_id:
        return

    user_id = update.effective_user.id
    text = update.message.text

    # Проверяем, является ли пользователь allowed_user_id и отвечает ли он на сообщение
    if user_id == allowed_user_id and update.message.reply_to_message:
        replied_user_id = update.message.reply_to_message.from_user.id
        process_user_score(replied_user_id, text, update)
    else:
        process_user_score(user_id, text, update)

def process_user_score(user_id, text, update):
    # Регулярное выражение для поиска чисел, обозначающих пункты и значения, допускающее пробелы и отсутствие причины
    match = re.search(r'(-?\d+)🟢\s*(\d{1,2})\.?\s*(.*)', text)

    if match is not None:
        user_id = str(user_id)
        value = int(match.group(1))
        point_number = int(match.group(2))

        if not 1 <= point_number <= 18:
            update.message.reply_text('Такого пункта нет! Номер пункта должен быть от 1 до 18.')
            return

        if not os.path.isfile(f'sums_{user_id}.json'):
            with open(f'sums_{user_id}.json', 'w') as file:
                json.dump({}, file)

        with open(f'sums_{user_id}.json', 'r') as file:
            data = json.load(file)

        data[str(point_number)] = data.get(str(point_number), 0) + value

        with open(f'sums_{user_id}.json', 'w') as file:
            json.dump(data, file)

        sorted_data = {k: v for k, v in sorted(data.items(), key=lambda item: int(item[0]))}
        point_values = [f"{k}. {v}" for k, v in sorted_data.items()]
        sum_values = sum(sorted_data.values())

        custom_message = get_custom_message(point_number, sum_values)
        if custom_message:
            update.message.reply_text(custom_message)
        else:
            update.message.reply_text('\n'.join(point_values + [f'Сумма всех пунктов: {sum_values}']))
    else:
        update.message.reply_text('Чтобы ваше сообщение было правильно обработано, оно должно соответствовать следующему формату:\n'
                                  '1️⃣ Отрицательное или положительное число, за которым следует зеленый кружок (🟢).\n'
                                  '2️⃣ Затем должна идти цифра, обозначающая номер пункта (от 1 до 18), с точкой или без.\n'
                                  '3️⃣ Причина является необязательной.\n'
                                  'Примеры:\n'
                                  '   "10🟢 3. Причина за что вы начисляете"\n'
                                  '   "10🟢 3"\n'
                                  '   "10🟢3. Причина"\n'
                                  '   "10🟢3"')

def set_custom_message(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 4:
        update.message.reply_text('Неверное количество аргументов. Используйте: /set (пункт) (количество баллов) (тег пользователя) (сообщение)')
        return

    point_number = int(args[0])
    score_threshold = int(args[1])
    user_tag = args[2]
    message = ' '.join(args[3:])

    custom_messages = {}
    if os.path.isfile('custom_messages.json'):
        with open('custom_messages.json', 'r') as file:
            custom_messages = json.load(file)

    custom_messages[point_number] = {'score_threshold': score_threshold, 'user_tag': user_tag, 'message': message}

    with open('custom_messages.json', 'w') as file:
        json.dump(custom_messages, file)

    update.message.reply_text(f'Настроенное сообщение для пункта {point_number} сохранено.')
    context.bot.send_message(update.effective_chat.id, f'Настроенное сообщение для пункта {point_number}:\n{user_tag} {message}')

def get_custom_message(point_number, total_score):
    if os.path.isfile('custom_messages.json'):
        with open('custom_messages.json', 'r') as file:
            custom_messages = json.load(file)
            if str(point_number) in custom_messages:
                if total_score >= custom_messages[str(point_number)]['score_threshold']:
                    return custom_messages[str(point_number)]['message']
    return None

def top_scores(update: Update, context: CallbackContext) -> None:
    top_data = {}
    bot = context.bot

    for filename in os.listdir('.'):
        if filename.startswith('sums_') and filename.endswith('.json'):
            with open(filename, 'r') as file:
                data = json.load(file)
                user_id = filename.split('_')[1].split('.')[0]

                try:
                    user = bot.get_chat(user_id)
                    username = user.username if user.username else user.first_name
                    total_score = sum(data.values())
                    top_data[username] = total_score
                except Unauthorized as e:
                    logger.warning(f"Unauthorized access for user ID: {user_id}, error: {e}")
                    continue
                except BadRequest as e:
                    logger.warning(f"BadRequest error for user ID: {user_id}, error: {e}")
                    continue
                except Exception as e:
                    logger.error(f"An error occurred for user ID: {user_id}, error: {e}")
                    continue

    sorted_top = sorted(top_data.items(), key=lambda item: item[1], reverse=True)
    if sorted_top:
        top_message = "\n".join([f"Ник: @{username}: {score}" for username, score in sorted_top])
    else:
        top_message = "Нет данных для отображения."

    update.message.reply_text(top_message)
