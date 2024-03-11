import json
import telebot
from telebot import types
import random


bot = telebot.TeleBot('your bot token')
user_data_file = 'user_data.json'


try:
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}


def save_user_data():
    with open(user_data_file, 'w', encoding='utf-8') as file:
        json.dump(user_data, file)



@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. '
                                      f'Сейчас я расскажу тебе как меня использовать. '
                                      f'Сначала заполни информацию о себе, нажми /getinfo чтобы начать')


@bot.message_handler(commands=['getinfo'])
def get_name(message):
    bot.send_message(message.chat.id, 'Напиши своё имя так, чтобы тебя узнали друзья')
    bot.register_next_step_handler(message, remember_name)


def remember_name(message):
    user_id = message.from_user.id
    name = message.text
    user_data[user_id] = {'name': name}
    bot.send_message(message.chat.id, 'Давай продолжим, нажми /wish_list')


@bot.message_handler(commands=['wish_list'])
def get_wishlist(message):
    bot.send_message(message.chat.id, 'Напиши, что бы ты хотел получить от друзей')
    bot.register_next_step_handler(message, remember_wishlist)


def remember_wishlist(message):
    user_id = message.from_user.id
    wish_list = message.text
    user_data[user_id]['wish_list'] = wish_list
    bot.send_message(message.chat.id, 'Давай продолжим, нажми /unwanted')


@bot.message_handler(commands=['unwanted'])
def get_unwanted(message):
    bot.send_message(message.chat.id, 'Напиши, что бы ты НЕ ХОТЕЛ получить от друзей')
    bot.register_next_step_handler(message, remember_unwanted)


def remember_unwanted(message):
    user_id = message.from_user.id
    unwanted = message.text
    user_data[user_id]['unwanted'] = unwanted
    bot.send_message(message.chat.id, 'Поздравляю! теперь тебе доступно меню игрока нажми /menu')


@bot.message_handler(commands=['menu'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Рестарт')
    btn2 = types.KeyboardButton('Анкета')
    btn3 = types.KeyboardButton('Узнать подопечного')
    btn4 = types.KeyboardButton('Посмотреть список участников')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'В меню можно посмотреть список участников либо заново пройти анкетирование', reply_markup=markup)



@bot.message_handler(func=lambda message: message.text=='Рестарт')
def restart(message):
    main(message)



@bot.message_handler(func=lambda message: message.text=='Посмотреть список участников')
def amount_users(message):
    a = tuple(map(lambda x: x['name'], user_data.values()))
    b = '\n'.join(a)
    c = len(a)
    bot.send_message(message.chat.id, f'{b}')
    bot.send_message(message.chat.id, f'Количество участников: {c}')


@bot.message_handler(func=lambda message: message.text=='Анкета')
def account(message):
    user_id = str(message.from_user.id)
    try:
        bot.send_message(message.chat.id, f'Имя: {user_data.get(user_id, {}).get("name", "Не предоставлено")}\nВишлист: {user_data.get(user_id, {}).get("wish_list", "Не предоставлено")}\nНе следует дарить: {user_data.get(user_id, {}).get("unwanted", "Не предоставлено")}')
    except KeyError:
        bot.send_message(message.chat.id, 'Анкета не готова')


@bot.message_handler(func=lambda message: message.text=='Узнать подопечного')
def ward(message):
    user_id = str(message.from_user.id)
    try:
        bot.send_message(message.chat.id, f'Твой подопечный: {user_data[str(user_data[user_id]["ward"])]["name"]}\nВишлист подопечного: {user_data.get(str(user_data[user_id]["ward"]), {}).get("wish_list", "-")}\nНе следует дарить: {user_data.get(str(user_data[user_id]["ward"]), {}).get("unwanted", "-")}')
    except KeyError:
        bot.send_message(message.chat.id, 'Жеребьёвка не проведена, ожидайте')




@bot.message_handler(commands=['play'])
def play(message):
    a = list(user_data.keys())
    b = list(user_data.keys())
    flag = True
    c = 0
    while flag:
        random.shuffle(a)
        for i in range(len(b)):
            if a[i] == b[i]:
                c += 1
        if c != 0:
            flag = True
            c = 0
        else:
            flag = False

    for i in range(len(a)):
        user_data[b[i]]['ward'] = a[i]


    bot.send_message(message.chat.id, 'Жеребьёвка проведена!')


@bot.message_handler(commands=['newsletter'])
def send_newsletter(message):
    for user_id in user_data:
        bot.send_message(user_id, f'Твой подопечный: {user_data[str(user_data[user_id]["ward"])]["name"]}\nВишлист подопечного: {user_data.get(str(user_data[user_id]["ward"]), {}).get("wish_list", "-")}\nНе следует дарить: {user_data.get(str(user_data[user_id]["ward"]), {}).get("unwanted", "-")}')
    bot.send_message(message.chat.id, 'Рассылка произведена!')

@bot.message_handler(commands=['wardmy'])
def get_unwanted(message):
    user_id = str(message.from_user.id)
    user_data[user_id]["ward"] = "497936489"
    bot.send_message(message.chat.id, 'Готово')


if __name__ == '__main__':
    try:
        bot.polling(timeout=50)
    finally:
        save_user_data()






bot.polling(none_stop=True)
