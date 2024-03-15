import logging
import sqlite3
import sys
import time
import telebot
import geocoder
from keyboards import main_menu_kb, new_dtp_kb
from secrets_data import BOT_TOKEN, MAP_API
from database import Users, IntegrityError, db_users_dtp, Location, db_location, db_submessage, SubMessage
from datetime import datetime

bot = telebot.TeleBot(BOT_TOKEN)

with db_users_dtp:
    db_users_dtp.create_tables([Users])

with db_location:
    db_location.create_tables([Location])

with db_submessage:
    db_submessage.create_tables([SubMessage])


def get_address_from_coordinates(): # Функция для заполнения параметров
    try:
        adr = geocoder.ip('me')
        return adr.address
    except Exception as exc:
        return 'Ошибка получения адреса!' # Если не смогли получить, возвращаем ошибку


@bot.message_handler(commands=['start'])
def welcome(message):
    """
    Функция, предназначенная для регистрации в базе данных бота новых пользователей, а также для приветствия старых
    :param message: str (команда "/start")
    :return:
    """
    try:
        Users.create(
            phone_number=message.contact,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            status=None,
            registration_data=datetime.now(),
            user_id=message.from_user.id,
        )
        hello_msg = bot.reply_to(message, '<b>{first_name}, Добро пожаловать! Для оформления ДТП используйте клавиатуру'
                                  ' ниже⬇️'.format(
                                    first_name=message.from_user.first_name),
                                 parse_mode='html',
                                 reply_markup=main_menu_kb)
        bot.register_next_step_handler(hello_msg, new_dtp)

    except IntegrityError:
        hello_msg = bot.reply_to(message, '<b>С возвращением, {first_name}!</b>'.format(
            first_name=message.from_user.first_name),
            parse_mode='html',
            reply_markup=main_menu_kb)
        bot.register_next_step_handler(hello_msg, new_dtp)


@bot.message_handler(content_types=['text'])
def new_dtp(message):
    if message.text == 'Новое ДТП \U0001F694':
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.reply_to(message,  'Передайте данные о ДТП. Все сообщения и фото будут привязаны к'
                            ' ДТП по высланной вами геолокации!\n\n\U00002757<b> Для передачи подробной текстовой '
                            'информации отправьте боту сообщение, которое будет начинаться со слова '
                            '"ДТП" </b>\U00002757',
                         parse_mode='html',
                         reply_markup=new_dtp_kb)
    elif message.text == 'Информация \U0001F4DD':
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        msg = bot.reply_to(message, 'Отправьте боту сообщение о том, как произошло ДТП!')
        bot.register_next_step_handler(msg, save_info)


@bot.message_handler(content_types=['location'])
def location(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if message.location is not None:
        current_position = (message.location.longitude, message.location.latitude) # Наши долгота и широта
        coordinates = f'{current_position[0]}, {current_position[1]}' # Координаты места ДТП
        address_str = get_address_from_coordinates() # Примерное место, где произошло ДТП

        # Заносим данные в базу данных
        Location.create(
            address=address_str,
            latitude=current_position[1],
            longitude=current_position[0],
        )

        bot.reply_to(message, 'Местоположение ДТП получено \U00002705\n\n<b>ДТП произошло по адресу:</b> {address}'
                              '\n\n<b>Координаты:</b> {coord}'.format(
                                        address=address_str,
                                        coord=coordinates),
                     parse_mode='html',
                     reply_markup=new_dtp_kb)
    else:
        bot.reply_to(message, 'Не смогли определить местоположение ДТП...\nПожалуйста, попробуйте отправить '
                              '<b>геолокацию</b> еще раз!',
                     parse_mode='html',
                     reply_markup=new_dtp_kb)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if message.photo:
        con = sqlite3.connect('information.db')  # Создание базы данных для фото
        cursor = con.cursor()  # Создаем курсор

        cursor.execute("""CREATE TABLE IF NOT EXISTS photos( 
        id INTEGER PRIMARY KEY,
        photo BLOB)""")  # Создаем таблицу
        file_path = bot.get_file(message.photo[0].file_id).file_path
        file = bot.download_file(file_path)
        image = message.photo # Полученное изображение
        print(image)

        with open('python1.png', 'wb') as photo:
            cursor.execute('INSERT INTO photos(photo) VALUES(?)', [photo.write(file)])

        con.commit()
        con.close()
        con.close()

        bot.reply_to(message, 'Фотография с места ДТП получена! \U0001F4F8', reply_markup=new_dtp_kb)


@bot.message_handler(content_types=['text'])
def save_info(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    SubMessage.create(
        message=message.text,
    )

    bot.send_message(message.chat.id, 'Информация о ДТП успешно получена! \U0001F58A', reply_markup=new_dtp_kb)


# @bot.message_handler(content_types=['text'])
# def create_dtp(message):
#     if message.text == 'Создать ДТП \U00002705':
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 2)
#         bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
#         bot.reply_to(message, 'ДТП успешно создано! \U0001F4DD', reply_markup=main_menu_kb)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """
    Обработчик сообщений echo_all
    :param message: принятое сообщение от пользователя
    :return: ответ бота
    """
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except:
        print('Сервер упал!')
        logging.error('error: {}'.format(sys.exc_info()[0]))
        time.sleep(5)