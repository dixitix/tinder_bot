from bot_launch import *
from get_profile import *
from start import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import state
import algorithm
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton


class Search(StatesGroup):
    flag = State()
    reaction = State()
    index = State()


async def iterate_it(message, candidates, index, state):
    if index < len(candidates):
        await Search.flag.set()
        async with state.proxy() as data:
            data['candidates'] = candidates
        await show(message, candidates, index, state)
    else:
        await start(message, 5)


@dp.message_handler(lambda message: message.text == "Начать поиск", state="*")
async def start_searching(message, state):
    candidates_info = db.choose_match(message.from_user.id)
    user_info = db.return_planets(message.from_user.id)
    candidates = algorithm.get_sorted_candidates(user_info, candidates_info)
    await iterate_it(message, candidates, 0, state)
    

@dp.message_handler(lambda message: message.text == "Остановить поиск", state="*")
async def stop_searching(message, state):
    await start(message, 2)
    await state.finish()  


@dp.message_handler(state=Search.flag)
async def show(message, candidates, index, state: FSMContext):
    candidate_profile = await get_other_profile(candidates[index])
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    like = KeyboardButton('❤')
    dislike = KeyboardButton('💔')
    stop = KeyboardButton('Остановить поиск')
    buttons.add(like, dislike, stop)
    async with state.proxy() as data:
        data['candidates'] = candidates
        data['index'] = index
    await Search.reaction.set()
    if candidate_profile[1] != 'none':
        await message.answer_photo(photo=candidate_profile[1], caption=candidate_profile[0], reply_markup=buttons)
    else:
        await message.answer(candidate_profile[0], reply_markup=buttons)
        

@dp.message_handler(state=Search.reaction)
async def reaction(message, state):
    async with state.proxy() as data:
            candidates = data['candidates']
            index = data['index']
            partner = candidates[index]
    if message.text == '❤':        
        await message.answer('Здорово!')
        await db.add_like(message.from_user.id, partner)
        if db.check_match(message.from_user.id, partner):
            await message.answer("У вас произошел мэтч! Просмотреть его можно в другом разделе.")
            await bot.send_message(partner, "У вас произошел мэтч! Скорее просмотрите его!")
        await state.finish() 
        await iterate_it(message, candidates, index + 1, state)
        return
    if message.text == '💔':  
        await message.answer('Как так?')
        await db.add_dislike(message.from_user.id, partner)
        await state.finish()
        await iterate_it(message, candidates, index + 1, state)
