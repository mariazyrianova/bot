import telebot
from telebot import types
import game
import menu
from menu import Menu
import fun

bot = telebot.TeleBot('5217964496:AAH26Km8eUv1uEDxOH30UQEADOvU_zje9pU')


@bot.message_handler(commands="start")
def command(message):
    chat_id = message.chat.id
    bot.send_sticker(chat_id, "CAACAgIAAxkBAAEE4FdilMT1PGIF9yQtJ4CFJ5Lhr8OJugACHQADwDZPE17YptxBPd5IJAQ")
    txt_message = f"Привет, {message.from_user.first_name}! Проведи время с пользой)"
    bot.send_message(chat_id, text=txt_message, reply_markup=Menu.getMenu(chat_id, "Главное меню").markup)


@bot.message_handler(content_types=['text'])
def get_messages(message):
    chat_id = message.chat.id
    ms_text = message.text

    cur_user = menu.Users.getUser(chat_id)
    if cur_user is None:
        cur_user = menu.Users(chat_id, message.json["from"])

    subMenu = menu.goto_menu(bot, chat_id, ms_text)
    if subMenu is not None:
        if subMenu.name == "Игра КНБ":
            gameRPS = game.newGame(chat_id, game.GameRPS())
            bot.send_photo(chat_id, photo=gameRPS.url_picRules, caption=gameRPS.text_rules, parse_mode='HTML')

        return

    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu is not None and ms_text in cur_menu.buttons:
        module = cur_menu.module

        if module != "":
            exec(module + ".get_text_messages(bot, cur_user, message)")

        if module == "Курс валют":
            course_bot(bot, chat_id)

        if ms_text == "Помощь":
            send_help(bot, chat_id)

    else:
        bot.send_message(chat_id, text="Прости, я не понимаю это: " + ms_text)
        menu.goto_menu(bot, chat_id, "Главное меню")

@bot.message_handler(content_types=['sticker'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    sticker = message.sticker
    bot.send_message(message.chat.id, sticker)


@bot.message_handler(content_types=['audio'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    audio = message.audio
    bot.send_message(message.chat.id, audio)


@bot.message_handler(content_types=['voice'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    voice = message.voice
    bot.send_message(message.chat.id, voice)


@bot.message_handler(content_types=['photo'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    photo = message.photo
    bot.send_message(message.chat.id, photo)


@bot.message_handler(content_types=['video'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    video = message.video
    bot.send_message(message.chat.id, video)


@bot.message_handler(content_types=['document'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    document = message.document
    bot.send_message(message.chat.id, document)
    if message.document.mime_type == "video/mp4":
        bot.send_message(message.chat.id, "Это GIF")


@bot.message_handler(content_types=['contact'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    contact = message.contact
    bot.send_message(message.chat.id, contact)


@bot.message_handler(content_types=['text'])
def get_messages(message):
    chat_id = message.chat.id
    ms_text = message.text

    cur_user = menu.Users.getUser(chat_id)
    if cur_user is None:
        cur_user = menu.Users(chat_id, message.json["from"])

    subMenu = menu.goto_menu(bot, chat_id, ms_text)
    if subMenu is not None:
        return

    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu is not None and ms_text in cur_menu.buttons:
        module = cur_menu.module

        if module != "":
            exec(module + ".get_text_messages(bot, cur_user, message)")

        if ms_text == "Помощь":
            send_help(bot, chat_id)

    else:
        bot.send_message(chat_id, text="Прости, но что это значит: " + ms_text)
        menu.goto_menu(bot, chat_id, "Главное меню")

def course_bot(bot, chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Курс_бот", url="https://t.me/")
    markup.add(btn1)

def send_help(bot, chat_id):
    bot.send_message(chat_id, "Автор: Зырянова Мария")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Напишите автору:", url="https://t.me/mary_zzzzzzz")
    markup.add(btn1)
    img = open('фото.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=markup)


bot.polling(none_stop=True, interval=0)