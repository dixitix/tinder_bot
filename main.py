import asyncio
import logging
import datetime
from aiogram import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import db
import re
import parser, algorithm
from get_profile import *
from bot_launch import *
from search import *
from matches import *
from geopy.geocoders import Nominatim


async def on_startup(_):
  await db.db_connect()


# Класс для анкеты
class Profile(StatesGroup):
  name = State()
  gender = State()
  birth_day = State()
  birth_month = State()
  birth_year = State()
  birth_hour = State()
  birth_minute = State()
  birth_city = State()
  city = State()
  preferences = State()
  photo = State()
  description = State()
  status = State()


# Заполенение анкеты
@dp.message_handler(lambda message: message.text == "Создать анкету",
                    state="*")
async def make_profile(message):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True,
                                input_field_placeholder="Введи свое имя/ник")
  if await db.user_exists(message.from_user.id):
    name = await db.get_name(message.from_user.id)
    info = KeyboardButton(str(name))
    buttons.add(info)
  buttons.add(back)
  await message.answer('Начнем заполнять анкету! Укажи свое имя/ник',
                       reply_markup=buttons)
  await Profile.name.set()


# Заполнение имени
@dp.message_handler(state=Profile.name)
async def fill_name(message, state):
  if str(message.text) == 'Назад':
    await state.finish()
    await start(message)
    return
  async with state.proxy() as data:
    data['name'] = message.text
    data['nickname_tg'] = message.from_user.username
  female = KeyboardButton('Женщина')
  male = KeyboardButton('Мужчина')
  non = KeyboardButton("Do not give a fuck")
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  buttons.add(female, male, non, back)
  await message.answer('Выбери свой гендер', reply_markup=buttons)
  await Profile.next()


# Заполнение гендера
@dp.message_handler(state=Profile.gender)
async def fill_gender(message, state):
  if str(message.text) == 'Назад':
    await Profile.name.set()
    message.text = ""
    await make_profile(message)
    return
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(
    one_time_keyboard=True,
    resize_keyboard=True,
    input_field_placeholder="Введи день своего рождения")

  if await db.user_exists(message.from_user.id):
    day_birth = await db.get_birth_day(message.from_user.id)
    info = KeyboardButton(str(day_birth))
    buttons.add(info)
  buttons.add(back)
  if message.text == 'Женщина' or message.text == 'Мужчина' or message.text == 'Do not give a fuck':
    async with state.proxy() as data:
      data['gender'] = message.text
    await message.answer(
      'Переходим к астрологической части! Укажи день своего рождения',
      reply_markup=buttons)
    await Profile.next()
    return
  female = KeyboardButton('Женщина')
  male = KeyboardButton('Мужчина')
  non = KeyboardButton("Do not give a fuck")
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  buttons.add(female, male, non, back)
  await message.answer('Пожалуйста, выбери гендер из доступных',
                       reply_markup=buttons)


# Заполнение дня рождения
@dp.message_handler(state=Profile.birth_day)
async def fill_day(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.name.set()
    user_data = await state.get_data()
    message.text = user_data['name']
    await fill_name(message, state)
    return
  if await db.user_exists(message.from_user.id):
    month_birth = await db.get_birth_month(message.from_user.id)
    info = KeyboardButton(str(month_birth))
    buttons.add(info)
  buttons.add(back)
  if message.text.isdigit() and 1 <= int(message.text) <= 31:
    async with state.proxy() as data:
      data['birth_day'] = int(message.text)
    buttons.input_field_placeholder = "Введи номер месяца рождения"
    await message.answer('Укажи номер месяца своего рождения',
                         reply_markup=buttons)
    await Profile.next()
  else:
    await message.answer('Пожалуйста, введи корректное число',
                         reply_markup=buttons)


# Заполнение месяца рождения
@dp.message_handler(state=Profile.birth_month)
async def fill_month(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.gender.set()
    user_data = await state.get_data()
    message.text = user_data['gender']
    await fill_gender(message, state)
    return
  if await db.user_exists(message.from_user.id):
    year_birth = await db.get_birth_year(message.from_user.id)
    info = KeyboardButton(str(year_birth))
    buttons.add(info)
  buttons.add(back)
  if message.text.isdigit() and 1 <= int(message.text) <= 12:
    async with state.proxy() as data:
      data['birth_month'] = int(message.text)
    buttons.input_field_placeholder = "Введи год своего рождения"
    await message.answer('Укажи год своего рождения', reply_markup=buttons)
    await Profile.next()
  else:
    await message.answer('Пожалуйста, введи корректный номер месяца',
                         reply_markup=buttons)


# Заполнение года рождения
@dp.message_handler(state=Profile.birth_year)
async def fill_year(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.birth_day.set()
    user_data = await state.get_data()
    message.text = str(user_data['birth_day'])
    await fill_day(message, state)
    return

  if await db.user_exists(message.from_user.id):
    hour = await db.get_birth_hour(message.from_user.id)
    minute = await db.get_birth_minute(message.from_user.id)
    info = KeyboardButton(str(hour) + ':' + f'{int(minute):02}')
    buttons.add(info)
  buttons.add(back)
  if (message.text.isdigit()
      and int(message.text) < 1920) or not message.text.isdigit():
    await message.answer('Пожалуйста, введи корректный год',
                         reply_markup=buttons)
    return

  isValidDate = True
  async with state.proxy() as data:
    day = data['birth_day']
    month = data['birth_month']
    year = int(message.text)
  try:
    datetime.datetime(int(year), int(month), int(day))
  except ValueError:
    isValidDate = False

  if (isValidDate):
    async with state.proxy() as data:
      data['birth_year'] = int(message.text)
    buttons.input_field_placeholder = "Введи время рождения"
    await message.answer('Укажи время рождения в формате чч:мм',
                         reply_markup=buttons)
    await Profile.next()
    return

  await message.answer(
    'К сожалению, введена некорректная дата. Начинаем заново!')
  await Profile.gender.set()
  user_data = await state.get_data()
  message.text = str(user_data['gender'])
  await fill_gender(message, state)


# Заполнение времени рождения
@dp.message_handler(state=Profile.birth_hour)
async def fill_time(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)

  if str(message.text) == 'Назад':
    await Profile.birth_month.set()
    user_data = await state.get_data()
    message.text = str(user_data['birth_month'])
    await fill_month(message, state)
    return

  if await db.user_exists(message.from_user.id):
    birth_city = await db.get_birth_city(message.from_user.id)
    info = KeyboardButton(str(birth_city))
    buttons.add(info)

  buttons.add(back)

  if re.fullmatch(r'[0-9]{1,2}:[0-9]{1,2}', message.text):
    hour = int(message.text.split(':')[0])
    minute = int(message.text.split(':')[1])
    if 0 <= hour <= 23 and 0 <= minute <= 59:
      async with state.proxy() as data:
        data['birth_hour'] = hour
      await Profile.next()
      async with state.proxy() as data:
        data['birth_minute'] = minute
      await Profile.next()
      buttons.input_field_placeholder = "Введи город рождения"
      await message.answer('Укажи город рождения', reply_markup=buttons)
    else:
      await message.answer('Пожалуйста, введи корректное время',
                           reply_markup=buttons)
  else:
    await message.answer('Пожалуйста, введи в формате чч:мм. Например 00:00',
                         reply_markup=buttons)


# Заполнение города рождения
@dp.message_handler(state=Profile.birth_city)
async def fill_birth_city(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.birth_year.set()
    user_data = await state.get_data()
    message.text = str(user_data['birth_year'])
    await fill_year(message, state)
    return

  if await db.user_exists(message.from_user.id):
    city = await db.get_city(message.from_user.id)
    info = KeyboardButton(str(city))
    buttons.add(info)
  if re.fullmatch(
      r'[а-яА-Я\-]*',
      message.text) and (len(db.select_city(message.text.capitalize())) > 0
                         or len(db.select_city(message.text))):
    async with state.proxy() as data:
      if len(db.select_city(message.text.capitalize())) > 0:
        data['birth_city'] = message.text.capitalize()
      else:
        data['birth_city'] = message.text
    buttons.input_field_placeholder = "Введи город проживания"
    location = KeyboardButton("Поделиться геопозицией", request_location=True)
    buttons.add(location, back)
    await message.answer(
      'С астрономической частью закончили! Осталась самая малость. Укажи город проживания',
      reply_markup=buttons)
    await Profile.next()
  else:
    buttons.add(back)
    await message.answer(
      'Пожалуйста, правильно введи название города. Пиши с заглавной буквы и на русском языке',
      reply_markup=buttons)


# Заполнение города проживания
@dp.message_handler(content_types=['location', 'text'], state=Profile.city)
async def fill_city(message, state):
  if str(message.text) == 'Назад':
    await Profile.birth_hour.set()
    user_data = await state.get_data()
    message.text = str(
      user_data['birth_hour']) + ":" + f"{int(user_data['birth_minute']):02}"
    await fill_time(message, state)
    return
  if message.content_type == 'location' or (
      len(db.select_city(message.text.capitalize())) > 0
      or len(db.select_city(message.text)) > 0):
    if message.content_type == 'location':
      lat = message.location.latitude
      lon = message.location.longitude
      coord = str(lat) + ', ' + str(lon)
      geolocation = Nominatim(user_agent="bot")
      location = geolocation.reverse(coord, language='ru')
      address = location.raw['address']
      city = address.get('city', '')
      async with state.proxy() as data:
        data['city'] = city
    else:
      async with state.proxy() as data:
        if len(db.select_city(message.text)):
          data['city'] = message.text
        else:
          data['city'] = message.text.capitalize()
    female = KeyboardButton('Женщин')
    male = KeyboardButton('Мужчин')
    non = KeyboardButton("Не важно")
    back = KeyboardButton("Назад")
    buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons.add(female, male, non, back)
    await message.answer(
      'Теперь выбери, кого ты предпочитаешь видеть в рекомендациях',
      reply_markup=buttons)
    await Profile.next()
  else:
    await message.answer(
      'Пожалуйста, введи корректное название города на русском языке')


# Заполнение предпочтений
@dp.message_handler(state=Profile.preferences)
async def fill_preferences(message, state):
  back = KeyboardButton("Назад")
  none = KeyboardButton("Без фотографии")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.birth_city.set()
    user_data = await state.get_data()
    message.text = user_data['birth_city']
    await fill_birth_city(message, state)
    return

  if await db.user_exists(message.from_user.id):
    if not await db.get_photo(message.from_user.id) == 'none':
      info = KeyboardButton('Оставить ранее прикрепленное фото')
      buttons.add(info)

  buttons.add(back, none)

  if message.text in [
      'Женщин', 'женщин', 'не важно', 'Мужчин', 'мужчин', 'Не важно'
  ]:
    async with state.proxy() as data:
      data['preferences'] = message.text.lower()
    await message.answer('Отлично!\nМожешь добавить фотографию!',
                         reply_markup=buttons)
    await Profile.next()
    return
  female = KeyboardButton('Женщин')
  male = KeyboardButton('Мужчин')
  non = KeyboardButton("Не важно")
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  buttons.add(female, male, non, back)
  await message.answer('Выбери, кого тебе показывать, из доступных вариантов',
                       reply_markup=buttons)


# Заполнение фото если нам скинули фото
@dp.message_handler(
  content_types=['photo', 'new_chat_photo', 'delete_chat_photo'],
  state=Profile.photo)
async def fill_photo_with(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.city.set()
    user_data = await state.get_data()
    message.text = user_data['city']
    await fill_city(message, state)
    return

  if await db.user_exists(message.from_user.id):
    info = KeyboardButton('Оставить ранее написанное описание')
    buttons.add(info)

  buttons.add(back)

  async with state.proxy() as data:
    data['photo'] = message.photo[0].file_id
  buttons.input_field_placeholder = "Напиши пару слов о себе"
  await message.answer(
    'Отлично!\nОсталось заполнить описание профиля.\nНапиши то, что считаешь важным\n️',
    reply_markup=buttons)
  await Profile.next()
  return


# Заполнение фото если нам не скинули фото
@dp.message_handler(content_types=['text'], state=Profile.photo)
async def fill_photo_without(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.city.set()
    user_data = await state.get_data()
    message.text = user_data['city']
    await fill_city(message, state)
    return

  if await db.user_exists(message.from_user.id):
    info = KeyboardButton('Оставить ранее написанное описание')
    buttons.add(info)

  buttons.add(back)

  if str(message.text) == 'Оставить ранее прикрепленное фото' or str(
      message.text) == 'Без фотографии':
    if str(message.text) == 'Оставить ранее прикрепленное фото':
      photo = await db.get_photo(message.from_user.id)
      async with state.proxy() as data:
        data['photo'] = photo
    else:
      async with state.proxy() as data:
        data['photo'] = "none"
    buttons.input_field_placeholder = "Напиши пару слов о себе"
    await message.answer(
      'Отлично!\nОсталось заполнить описание профиля.\nНапиши то, что считаешь важным\n️',
      reply_markup=buttons)
    await Profile.next()
    return
  back = KeyboardButton("Назад")
  none = KeyboardButton("Без фотографии")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  buttons.add(back, none)
  await message.answer('Такой формат не поддерживается :(',
                       reply_markup=buttons)


# Заполнение фото если нам скинули фигню
@dp.message_handler(content_types=[
  "audio", "document", "sticker", "video", "video_note", "voice", "location",
  "contact", "new_chat_members", "left_chat_member", "new_chat_title",
  "group_chat_created", "supergroup_chat_created", "channel_chat_created",
  "migrate_to_chat_id", "migrate_from_chat_id", "pinned_message"
],
                    state=Profile.photo)
async def fill_photo_rubbish(message, state):
  back = KeyboardButton("Назад")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  if str(message.text) == 'Назад':
    await Profile.city.set()
    user_data = await state.get_data()
    message.text = user_data['city']
    await fill_city(message, state)
    return
  back = KeyboardButton("Назад")
  none = KeyboardButton("Без фотографии")
  buttons = ReplyKeyboardMarkup(resize_keyboard=True)
  buttons.add(back, none)
  await message.answer('Такой формат не поддерживается :(',
                       reply_markup=buttons)


# Заполнение описания
@dp.message_handler(state=Profile.description)
async def fill_description(message, state):
  if str(message.text) == 'Назад':
    await Profile.preferences.set()
    user_data = await state.get_data()
    message.text = user_data['preferences']
    await fill_preferences(message, state)
    return

  if str(message.text) == 'Оставить ранее написанное описание':
    description = await db.get_description(message.from_user.id)
    async with state.proxy() as data:
      data['description'] = description
  else:
    async with state.proxy() as data:
      data['description'] = message.text

  await Profile.next()
  async with state.proxy() as data:
    data['status'] = 0

  await db.create_profile(state, message.from_user.id)
  user_data = await db.get_map_fields(message.from_user.id)
  planets_coordinates = parser.parsing(user_data)
  planets_degrees = algorithm.get_list_planets_degrees(planets_coordinates)
  db.fill_planets(message.from_user.id, planets_degrees)

  start_search = KeyboardButton("Начать поиск")
  stop = KeyboardButton("Сделать паузу")
  buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  buttons.add(start_search, stop)
  await message.answer('Здорово! Перейдем к поиску анкет!',
                       reply_markup=buttons)
  await state.finish()


# Удаление анкеты
@dp.message_handler(lambda message: message.text == "Удалить анкету",
                    state="*")
async def start_deleting(message):
  yes = KeyboardButton("Да, удалить анкету")
  no = KeyboardButton("Нет, оставить")
  buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
  buttons.add(yes, no)
  await message.answer('Ты уверен_а, что хочешь удалить анкету?',
                       reply_markup=buttons)


@dp.message_handler(lambda message: message.text == "Да, удалить анкету",
                    state="*")
async def delete(message):
  await db.delete_profile(message.from_user.id)
  markup = ReplyKeyboardRemove()
  await start(message, 6)


@dp.message_handler(lambda message: message.text == "Нет, оставить", state="*")
async def remain(message):
  await start(message, 1)


#Изменение анкеты
@dp.message_handler(lambda message: message.text == "Изменить анкету",
                    state="*")
async def change_profile(message):
  status = db.check_user(message.from_user.id)
  if status == 0:
    yes = KeyboardButton("Да, заморозить анкету")
    no = KeyboardButton("Нет, не нужно")
    buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons.add(yes, no)
    await message.answer(
      'Сейчас будем изменять анкету. Может быть, ты хочешь заморозить анкету? Тогда ее не увидят другие пользователи и у тебя не появятся новые мэтчи',
      reply_markup=buttons)
  else:
    yes = KeyboardButton("Да, разморозить анкету")
    no = KeyboardButton("Нет, оставить заморозку")
    buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons.add(yes, no)
    await message.answer(
      'Сейчас будем изменять анкету. Может быть, ты хочешь разморозить анкету? Тогда ее смогут видеть другие пользователи',
      reply_markup=buttons)


# заморозить анкету
@dp.message_handler(lambda message: message.text == "Да, заморозить анкету",
                    state="*")
async def freezing(message):
  if await db.user_exists(message.from_user.id):
    db.freeze_user(message.from_user.id)
    await message.answer('Заморозил! Теперь твою анкету никто не увидит'
                         )  # заморозка включена
    message.text = "Создать анкету"
    await make_profile(message)
  else:
    await message.answer('Сначала создай анкету')
    await start(message, 0)


@dp.message_handler(lambda message: message.text == "Нет, не нужно", state="*")
async def not_freeze(message):
  await message.answer('Здорово! Тогда продолжаем')
  message.text = "Создать анкету"
  await make_profile(message)


# Разморозить анкету
@dp.message_handler(lambda message: message.text == "Да, разморозить анкету",
                    state="*")
async def freezing(message):
  if await db.user_exists(message.from_user.id):
    db.unfreeze_user(message.from_user.id)
    await message.answer(
      'Разморозил! Теперь твою анкету смогут видеть другие пользователи')
    message.text = "Создать анкету"
    await make_profile(message)
  else:
    await message.answer('Сначала создай анкету')
    message.text = "Создать анкету"
    await make_profile(message)


@dp.message_handler(lambda message: message.text == "Нет, оставить заморозку",
                    state="*")
async def not_unfreeze(message):
  await message.answer('Услышал! Тогда продолжаем')
  message.text = "Создать анкету"
  await make_profile(message)


@dp.message_handler(commands=['help'], state='*')
async def help(message):
  await message.answer(
    f'Если ты еще не заполнил_а анкету, скорее жми кнопку "Создать анкету".\nТеперь можешь нажать /menu, чтобы увидеть весь функционал.\n\nТы можешь посмотреть свою анкету, изменить или удалить ее.\nЧтобы посмотреть анкеты других пользователей, нажми "Начать поиск".\nСинастрии с людьми, с которыми случился взаимный лайк, можно увидеть в "Посмотреть мэтчи".'
  )


@dp.message_handler(commands=['menu'], state='*')
async def menu(message):
  await start(message, 7)


if __name__ == "__main__":
  executor.start_polling(dispatcher=dp, on_startup=on_startup)
