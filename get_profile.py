import asyncio
import db
from bot_launch import *
import compatibility
from aiogram.types.message import ParseMode
from datetime import date
import datetime as dt

@dp.message_handler(lambda message: message.text == "Посмотреть анкету",
                    state="*")
async def show_profile(message):
    profile = await db.get_profile(message.from_user.id)
    name = profile[1]
    gender = profile[2]
    birth_day = profile[3]
    birth_month = profile[4]
    birth_year = profile[5]
    birth_hour = profile[6]
    birth_minute = profile[7]
    birth_city = profile[8]
    city = profile[9]
    preferences = profile[10]
    description = profile[12]
    status = profile[24]

    if status == 0:
        description_status = 'не заморожена'
    else:
        description_status = 'заморожена'
    
    if str(preferences) == 'не важно' or str(preferences) == 'Не важно':
        preferences = 'людей всех гендеров'

    gender = str(gender).lower()


    text_in_message =  f'Это твоя анкета🌟\n\n🌖' + '* Имя:   *' + f'{name}\n🌗' + '* Гендер:   *'  + f'{gender}\n🌘'  +  '* Дата рождения:   *' + f'{birth_day}.{birth_month:02}.{birth_year} \n🌑'  + f'* Время рождения:   *{birth_hour}' + ':' + f'{int(birth_minute):02}' + f'\n🌒* Город рождения:   *{birth_city}\n🌓* Местоположение:   *{city}\n🌔* Описание:   *{description}' + f'\n\n🔮 Я показываю тебе анкеты {preferences}\n🗒 Твоя анкета сейчас {description_status}'

    db_photo = await db.get_photo(message.from_user.id)
    if db_photo != 'none':
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=db_photo,
            caption=text_in_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer(text_in_message, parse_mode=ParseMode.MARKDOWN)

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


async def get_other_profile(id):
    profile = await db.get_profile(id)
    name = profile[1]
    gender = profile[2]
    city = profile[9]
    description = profile[12]
    day_birth = profile[3]
    month_birth = profile[4]
    year_birth = profile[5]

    date_birth = dt.datetime(year_birth, month_birth, day_birth)

    age = calculate_age(date_birth)
    
    db_photo = profile[11]
    caption = f'{name}, {age}, {city} \n\n{description}'
    return [caption, db_photo]



async def get_profile_match(id1, id2):
   
    nickname2 = await db.get_username(id2)
    # name2 = f"[{nickname2}](tg://user?id={id2})"
    name2 = f'@{nickname2}'

    user1_data = await db.get_map_fields(id1)
    user2_data = await db.get_map_fields(id2)
    photo = compatibility.get_compatibility(user1_data, user2_data)

    caption = f'Вот ваша общая синастрия с {name2}! \n\nСкорее начинай диалог :)'

    return [caption, photo]
