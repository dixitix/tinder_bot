from bot_launch import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import db


@dp.message_handler(commands=['start'], state='*')
async def start(message, change_text=0):
    options = ReplyKeyboardMarkup(resize_keyboard=True)
    search = KeyboardButton('Начать поиск')
    make_profile = KeyboardButton('Создать анкету')
    watch_profile = KeyboardButton('Посмотреть анкету')
    watch_matches = KeyboardButton('Посмотреть мэтчи')
    change_profile = KeyboardButton('Изменить анкету')
    delete_profile = KeyboardButton('Удалить анкету')

    if await db.user_exists(message.from_user.id):
        options.add(search, watch_profile, watch_matches, change_profile, delete_profile)
    else:
        options.add(make_profile)
    if change_text == 0:
        text = f'Привет, {message.from_user.first_name}! Помогу найти вторую половинку по твоей натальной карте!'
    elif change_text == 1:
       text = 'Снова ты! Помогу найти вторую половинку по твоей натальной карте!'
    elif change_text == 2:
        text = 'Надоело искать? Понимаю тебя...'
    elif change_text == 3:
        text = 'Тут будут отображаться твои будущие мэтчи, пока здесь пусто :('
    elif change_text == 4:
        text = 'Услышал тебя! Можешь продолжить смотреть свои мэтчи в любой момент.'
    elif change_text == 5:
        text = 'На этом пока все. Загляни сюда позже!'
    elif change_text == 6:
        text = 'Жаль..... Ты сможешь заново создать анкету, если захочешь.'
    elif change_text == 7:
        text = 'Вот главное меню. Нажми /help, если не знаешь, как пользоваться ботом.'
    await message.answer(text, reply_markup=options)
