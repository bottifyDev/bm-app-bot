import logging
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
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.deep_linking import decode_payload
from aiogram.types.web_app_info import WebAppInfo
from tgbot.config import Config
from tgbot.db.api import *
from api import *
#########################################
console = Console(color_system="256")
arrow = Emoji('arrow_right')

# STATES
class Token(StatesGroup):
    EditToken = State()

def start_text(name):
	return f"<b>Добро пожаловать, {name}!</b>\n\n<em>💬 Бот для проверки заявок в базе клиентов</em>"

def remove_keyboard():
	markup = ReplyKeyboardRemove()
	return markup

# Menu
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    time_btn = KeyboardButton(text="Проверка заявки")
    markup.row(time_btn)
    return markup


# Auth Start
async def auth_start(message: Message, state: FSMContext):
	""" '/start'
	"""
	args = message.get_args()
	if args:
		addToken(message.chat.id,args)
	customer = regCustomer(message.chat.id, message.chat.full_name)
	# Выводим лог сообщение
	console.log(f"{customer.forLog} {arrow} {dict(msg=message.text)}")
	# Отвечаем сообщением и главным меню
	check = check_api_token(customer.token)
	if check == False:
		check_text = f"<em>\n💬  Токен не зарегистрирован в системе. Для добавления токена,\nнажмите /add_token</em>"
	else:
		check_text = f"{check}"
	text = f"{start_text(customer.name)}\n{check_text}"
	await message.answer(text, reply_markup=main_menu())
	await state.reset_state()

# Auth Dp
async def auth_dp(call: CallbackQuery, state: FSMContext):
	""" Callback data 'menu'
	"""
	# Находим/Регистрируем юзера
	customer = regCustomer(call.message.chat.id, call.message.chat.full_name)
	# Выводим лог сообщение
	console.log(f"{customer.forLog} {arrow} {dict(cb=call.data)}")
	# Закрываем коллбэк и редактируем сооющение
	await call.answer(cache_time=1, text="!")
	await call.message.edit_text(start_text(customer.name))

# Add token
async def add_token(message: Message, state: FSMContext):
	""" '/add_token'
	"""
	# Находим/Регистрируем юзера
	customer = regCustomer(message.chat.id, message.chat.full_name)
	# Выводим лог сообщение
	console.log(f"{customer.forLog} {arrow} {dict(msg=message.text)}")
	current_token = getToken(message.chat.id)
	check = check_api_token(current_token)
	if check == False:
		check_text = "Такой токен не зарегистрирован с CRM"
	else:
		check_text = f"{check}"
	await Token.EditToken.set()
	await message.answer(f"<b>Текущий токен</b> <code>{current_token}</code>\n{check_text}\n-------------------------\n<em>💬 Укажите новый токен\nили нажмите /start для отмены</em>",reply_markup=remove_keyboard())

async def token_dp(message: Message, state: FSMContext):
	if message.text == "/cancel":
		await message.answer(f"<em>Отменено</em>",reply_markup=main_menu())
		await state.reset_state()
	else:
		check = check_api_token(message.text)
		if check == False:
			check_text = "<em>не зарегистрирован в системе, чтобы изменить токен\nнажмите /add_token</em>"
		else:
			check_text = f"{check}"
		token = addToken(message.chat.id,message.text)
		await message.answer(f"<em>💬 Токен</em> <code>{token}</code>\n{check_text}",reply_markup=main_menu())
		await state.reset_state()

# DP
def register_auth(dp: Dispatcher):
	"""Main Dispatcher
	"""
	dp.register_message_handler(auth_start, commands=["start"], state="*")
	dp.register_callback_query_handler(auth_dp, text_contains="menu", state="*")
	dp.register_message_handler(add_token, commands=["add_token"], state="*")
	dp.register_message_handler(token_dp, state=Token.EditToken)
	dp.register_message_handler(token_dp, commands=["cancel"], state=Token.EditToken)











