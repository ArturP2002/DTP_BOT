import telebot

# Главное меню пользователя для выбора действий
main_menu_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
new_dtp_but = telebot.types.KeyboardButton(text='Новое ДТП \U0001F694')
balance_but = telebot.types.KeyboardButton(text='Баланс \U0001F4B0')
main_menu_kb.add(new_dtp_but)
main_menu_kb.add(balance_but)

# Клавиатура для создания ДТП
new_dtp_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
geolocation = telebot.types.KeyboardButton(text='Геолокация \U0001F30F', request_location=True)
create_dtp = telebot.types.KeyboardButton(text='Создать ДТП \U00002705')
cancel = telebot.types.KeyboardButton(text='Отмена \U0000274C')
information = telebot.types.KeyboardButton(text='Информация \U0001F4DD')
new_dtp_kb.add(geolocation)
new_dtp_kb.add(create_dtp, cancel)
new_dtp_kb.add(information)