import wikipedia
import telebot

wikipedia.set_lang('ru')
bot = telebot.TeleBot('5130981455:AAGjRfUaBhRCWumUuIqW2Ezfng87y-od17A')

@bot.message_handler(commands=['start'])
def start(message):
    sending_mess = f"<b>Привет {message.from_user.first_name}!</b>\nЧтобы приступить к поиску введите нужное слово и получите ваш ответ"
    bot.send_message(message.chat.id, sending_mess, parse_mode='html')

@bot.message_handler(content_types=['text'])
def mess(message):
    word = message.text.strip().lower()
    try:
        final_message = wikipedia.summary(word)
    except wikipedia.exceptions.PageError:
        final_message = ""
    bot.send_message(message.chat.id, final_message, parse_mode="html")

bot.polling(none_stop=True)
