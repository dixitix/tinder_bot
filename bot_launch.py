from aiogram import Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token='5719025242:AAFaiDkCGai4U9ZxeTgAXIixKS1HC9ZVHi4')
dp = Dispatcher(bot, storage=MemoryStorage())
