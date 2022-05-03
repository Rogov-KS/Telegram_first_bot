import telebot
import config
import random
import requests
from datetime import datetime
from telebot import types
from pycbrf import ExchangeRates
from time import sleep
from bs4 import BeautifulSoup
bot = telebot.TeleBot(config.TOKEN)

cripto_response = ''
@bot.message_handler(commands=['start'])
def welcome(message):
    global cripto_response
    cripto_response = requests.get(url='https://bitinfocharts.com/ru/crypto-kurs/')

    sti = open('stickers/Greatings.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🎲 Рандомное число")
    item2 = types.KeyboardButton("😊 Как дела?")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     f"Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>{bot.get_me().first_name}</b>, бот созданный чтобы быть подопытным кроликом.",
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['rates'])
def rates(message):
    currency = ["RUB", "USD", "EUR", "CNY"]
    sti = open('stickers/Thinking.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)
    sleep(5)
    text_ans = ''
    rates = ExchangeRates(datetime.now())
    for curen in currency:
        if not rates[curen] is None:
            text_ans += f'<b>{curen}</b> rate now is {float(rates[curen].rate)}\n'
        else:
            text_ans += f'Has no information about <b>{curen}</b>\n'

    bot.send_message(message.chat.id, text=text_ans, parse_mode='html')


@bot.message_handler(commands=['cripto_rates'])
def rates(message):
    global cripto_response
    soup = BeautifulSoup(cripto_response.text, 'lxml')
    ans_text = soup.find("tr", id="tr_1").find_all('td')
    for td_item in ans_text:
        if td_item.get("data-val") == "BTC":
            ans_text = td_item.find_next_sibling()
            break

    ans_text = ans_text.get("data-val")

    bot.send_message(message.chat.id, text=f"BTC costs {ans_text}$ now", parse_mode='html')

@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == '🎲 Рандомное число':
            bot.send_message(message.chat.id, str(random.randint(0, 100)))
        elif message.text == '😊 Как дела?':

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
            item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')

            markup.add(item1, item2)

            bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)
        else:
            sti = open('stickers/NoIdeaToDo.tgs', 'rb')
            bot.send_sticker(message.chat.id, sti)

            bot.send_message(message.chat.id, 'Неправильная команда.\n/help вам в помощь)')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!11")

    except Exception as e:
        print(repr(e))


# RUN
bot.polling(none_stop=True)