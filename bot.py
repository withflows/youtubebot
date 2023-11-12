import os
import telebot
from pytube import YouTube
import requests
import random
import json
import time
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TOKEN')
admin = os.getenv('ADMIN')
errorchat = os.getenv('ERRORCHAT')

TOKEN = f'{token}'

chat_id = -1002083924192
user_id = 0

try:
    with open('database.txt', 'rb') as file:
        bot_data = json.load(file)
except FileNotFoundError:
    bot_data = {}

adv = [
f'[Аниме Токийский гуль](t.me/tokyoghoulp)\n\nВозникла ошибка? [Пишите](t.me/withflow)',
f'[Аниме Реинкарнация Безработного](t.me/MushokuTenseiAll)\n\nВозникла ошибка? [Пишите](t.me/withflow)', f'[Аниме Сага о Винланде](https://t.me/+N4mxapoDJ3MwMTg1)\n\nВозникла ошибка? [Пишите](t.me/withflow)'
]

random_adv = random.choice(adv)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    # Проверяем, подписан ли пользователь на канал
    if str(user_id) not in bot_data:
        bot_data[str(user_id)] = True  # Добавляем пользователя в базу данных
        with open('database.txt', 'w') as file:
            json.dump(bot_data, file)  # Сохраняем базу данных в файл
    
    if is_subscribed(chat_id, user_id):
        bot.reply_to(message, "Вы уже подписаны на канал. Можете отправлять ссылки на видео.")
    else:
        bot.reply_to(message, f'Подпишитесь на [канал](t.me/anime_announce), чтобы начать использовать бота.', parse_mode= 'Markdown')

def is_subscribed(chat_id, user_id):
    # Замените <YOUR_BOT_TOKEN> на ваш токен бота
    bot_token = TOKEN
    # Запрос к Telegram API для получения информации о пользователе в канале
    response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getChatMember', params={
        'chat_id': chat_id,
        'user_id': user_id
    })
    
    if response.status_code == 200:
        result = response.json()
        
        # Проверяем статус подписки пользователя на канал
        if result['result']['status'] in ['creator', 'administrator', 'member']:
            return True
    	
    # Если запрос не удался или пользователь не подписан на канал, возвращаем False
    return False

@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.from_user.id  # Получаем ID пользователя
    # Проверяем, является ли пользователь админом
    if user_id == 5675650954:
        bot.reply_to(message, 'Количество пользователей: {}'.format(len(bot_data)))
    else:
        bot.reply_to(message, 'У вас нет доступа к этой команде.')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    
    if 'last_reply' in globals():
        elapsed_time = time.time() - globals()['last_reply']
        if elapsed_time < 5:
            remaining_time = int(5 - elapsed_time)
            bot.reply_to(message, f"Подождите {remaining_time} секунд перед тем, как отправить следующий запрос")
            
            return
    globals()['last_reply'] = time.time()
    		
    if is_subscribed(chat_id, user_id):
        # Пытаемся скачать видео по ссылке     
        bot.send_message(message.chat.id, "Дождитесь полной загрузки видео...")
        try:
            video_url = message.text
            youtube = YouTube(video_url)
            video = youtube.streams.get_highest_resolution()
            
            # Проверяем размер видео
            if video.filesize > 400000000:  # 400 МБ в байтах
                bot.reply_to(message, "Размер видео слишком большой для бота, вы можете [поддержать](t.me/withflow) проект, чтобы я смог увеличить размер загружаемых видео", parse_mode= 'Markdown')
            else:
                video.download()
                bot.send_video(message.chat.id, open(video.default_filename, 'rb'), caption = random_adv, parse_mode= 'Markdown')
                # Удаляем загруженное видео
                os.remove(video.default_filename)
        
        except Exception as e:
            bot.reply_to(message, "Не удалось скачать видео. Попробуйте еще раз.")
            try:
            	bot.send_message(admin, f'При обработке сообщения от [пользователя](tg://openmessage?user_id={user_id}) возникла ошибка: {e}', parse_mode= 'Markdown')
            except Exception as e:
            	bot.send_message(errorchat, f'_{e}_\n\n[Задать вопрос](tg://openmessage?user_id={user_id})', parse_mode= 'Markdown')
    
    else:
        bot.reply_to(message, f'Вы все еще не подписаны на [канал](t.me/anime_announce), подпишитесь, чтобы начать использовать бота.', parse_mode= 'Markdown')

# Запускаем бота
bot.polling()
