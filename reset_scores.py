import os
import shutil
from datetime import datetime
import json
from telegram import Update
from telegram.ext import CallbackContext

def reset_scores(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")
    current_folder = f'seasons/{current_date}_{current_time}'

    os.makedirs(current_folder)

    current_files = [file for file in os.listdir('.') if os.path.isfile(file) and file.endswith('.json')]

    for file in current_files:
        shutil.move(file, f'{current_folder}/{file}')

    update.message.reply_text('Все баллы обнулены и перенесены в новую папку.')
