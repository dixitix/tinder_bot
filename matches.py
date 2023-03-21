from bot_launch import *
from get_profile import get_profile_match
from start import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import state
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton


class Matches(StatesGroup):
    active = State()
    match = State()


async def iterate_it(message, matches, index, state):
    if index < len(matches):
        await Matches.active.set()
        async with state.proxy() as data:
            data['matches'] = matches
        await show_match(message, index, state)
    else:
        await start(message, 5)


@dp.message_handler(lambda message: message.text == "Посмотреть мэтчи", state="*")
async def start_showing(message, state):
    matches = db.get_matches(message.from_user.id)
    if len(matches) == 0:
        await start(message, 3)
        return
    await iterate_it(message, matches, 0, state)


@dp.message_handler(lambda message: message.text == "Продолжить позже", state="*")
async def stop_showing(message, state):
    await start(message, 4)


@dp.message_handler(state=Matches.active)
async def show_match(message, index, state):
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    next = KeyboardButton("Дальше")
    stop = InlineKeyboardButton('Продолжить позже')
    buttons.add(next, stop)
    async with state.proxy() as data:
        matches = data['matches']
        data['index'] = index
    match = matches[index]
    match_profile = await get_profile_match(message.from_user.id, match)
    
    db.mark_seen(message.from_user.id, match)
    await Matches.match.set()
    await bot.send_photo(message.chat.id, photo=match_profile[1], caption=match_profile[0], reply_markup=buttons)


@dp.message_handler(state=Matches.match)
async def next(message, state):
    if message.text != "Дальше":
        return
    async with state.proxy() as data:
        matches = data['matches']
        index = data['index']
    await state.finish()
    await iterate_it(message, matches, index + 1, state)
