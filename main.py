import os
import texts

from telegram import (Bot,
                      Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (Updater,
                          CommandHandler,
                          CallbackContext,
                          Filters,
                          MessageHandler,
                          CallbackQueryHandler,
                          ConversationHandler)
from telegram.utils.request import Request
from dotenv import load_dotenv
from validators import validate_result

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

CALLBACK_BUTTON3_YES = 'callback_button3_yes'
CALLBACK_BUTTON4_NO = 'callback_button4_no'
CALLBACK_BUTTON5_ACCOUNT = 'callback_button5_account'
CALLBACK_BUTTON6_GIFT = 'callback_button5_gift'

RES = 1
YES_OR_NO = 2

TITLES = {
    CALLBACK_BUTTON3_YES: 'Да',
    CALLBACK_BUTTON4_NO: 'Нет',
    CALLBACK_BUTTON5_ACCOUNT: 'Нажать для записи',
    CALLBACK_BUTTON6_GIFT: 'Подборка "ВкусВилл"',

}


def get_inline_keyboard_one_key(text, url):
    """Клавиатура с одной кнопкой"""
    keyboard = [
        [
            InlineKeyboardButton(text=text, url=url),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_inline_keyboard_two_key(text1, callback_data1, text2, callback_data2):
    """Клавиатура с двумя кнопками"""
    keyboard = [
        [
            InlineKeyboardButton(text=text1, callback_data=callback_data1),
            InlineKeyboardButton(text=text2, callback_data=callback_data2),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def do_start(update: Update, context: CallbackContext):
    """Старт диалога"""
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=texts.TEXT1_HI,
    )
    return RES


def result_handler(update: Update, context: CallbackContext):
    """Обработка присланного результата"""
    text = ''
    result = validate_result(text=update.message.text)
    if result is None:
        update.message.reply_text('Пожалуйста, укажи корректное колличество баллов в цифровом формате!')
        return RES
    elif 1 <= result <= 12:
        text = texts.TEXT2_GOOD
    elif 13 <= result <= 24:
        text = texts.TEXT2_BAD
    update.effective_message.reply_text(
        text=text,
        reply_markup=get_inline_keyboard_two_key(
            text1=TITLES[CALLBACK_BUTTON3_YES],
            callback_data1=CALLBACK_BUTTON3_YES,
            text2=TITLES[CALLBACK_BUTTON4_NO],
            callback_data2=CALLBACK_BUTTON4_NO,
        )
    )
    return YES_OR_NO


def keyboard_callback_handler(update: Update, context: CallbackContext):
    """Запись на консультацию или подарок"""
    query = update.callback_query
    data = query.data
    if data == CALLBACK_BUTTON3_YES:
        update.effective_message.reply_text(
            text=texts.TEXT3_CONSULTATION,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON5_ACCOUNT],
                url=texts.URL_ACCOUNT,
            ),
        )
    elif data == CALLBACK_BUTTON4_NO:
        update.effective_message.reply_text(
            text=texts.TEXT3_GIFT,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON6_GIFT],
                url=texts.URL_GIFT,
            ),
        )
    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны"""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /start')
    return ConversationHandler.END


def main():
    req = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
    )
    bot = Bot(
        token=TELEGRAM_TOKEN,
        request=req
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', do_start),
        ],
        states={
            RES: [
                MessageHandler(Filters.all, result_handler, pass_user_data=True),
            ],
            YES_OR_NO: [
                CallbackQueryHandler(callback=keyboard_callback_handler, pass_user_data=True)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ],
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
