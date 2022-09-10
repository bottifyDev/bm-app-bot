import logging
import json
from rich.console import Console
from rich.emoji import *
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import Message
from aiogram.dispatcher.filters import *
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from tgbot.config import Config
from tgbot.db.api import *
from api import *
#########################################
console = Console(color_system="256")
arrow = Emoji('arrow_right')

class SetCheckConfig(StatesGroup):
    InputSeconds = State()

async def admin_start(message: Message):
    await message.reply("Введите количество секунд для периода проверки")
    await SetCheckConfig.InputSeconds.set()

async def input_period_dp(message: Message, state: FSMContext):
    period = message.text
    new_period = setCheckConfig(period)
    console.log(new_period)
    await state.reset_state()
    await message.reply("Период установлен для выхода - нажмите /start")

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["period"], state="*", is_admin=True)
    dp.register_message_handler(input_period_dp, state=SetCheckConfig.InputSeconds)


