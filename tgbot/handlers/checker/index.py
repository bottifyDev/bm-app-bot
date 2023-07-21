import time
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


from ..auth.index import main_menu
from tgbot.config import Config
from tgbot.db.api import *
from api import *
from bl import *
#########################################
console = Console(color_system="256")
arrow = Emoji('arrow_right')

# STATES


class CheckByPhone(StatesGroup):
    InputNumber = State()

class CheckByName(StatesGroup):
    InputBrand = State()
    InputRegion = State()
    InputName = State()

def checker_title_text():
    return f"<b>✅ Проверка заявки</b>"

def checker_tips_text():
    return f"<em>💬 Вы можете проверить заявку по номеру телефона или по имени компании. Выберите необходимый фильтр 👇</em>"

def by_phone_text():
    return f"<b>📱 Проверка заявки по номеру телефона</b>\n\n<em>💬 Номер телефона вводится в формате</em> <code>79990001122</code>"

def by_name_text():
    return f"<b>📝 Проверка заявки по имени компании</b>"


def remove_keyboard():
    markup = ReplyKeyboardRemove()
    return markup


def checker_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    phone_btn = InlineKeyboardButton(
        text="📱 По номеру", callback_data="by_phone")
    company_btn = InlineKeyboardButton(
        text="📝 По имени", callback_data="by_name")
    markup.add(phone_btn, company_btn)
    return markup


def brands_menu(token):
    markup = InlineKeyboardMarkup(row_width=2)
    brands = get_brands(token)
    for brand in brands:
        brand_id = int(brand['id'])
        markup.row(InlineKeyboardButton(text=f"🏷 {brand['name']}", callback_data=f"brand:{brand_id}"))
    return markup

def regions_menu(token):
    markup = InlineKeyboardMarkup(row_width=1)
    regions = get_regions(token)
    for region in regions:
        region_id = region['id']
        markup.row(InlineKeyboardButton(text=f"🏙 {region['name']}", callback_data=f"r:{region_id}") )
    return markup

def brands_keyboard(brands: list):
    markup = InlineKeyboardMarkup(row_width=2)
    for brand in brands:
        brand_id = int(brand['id'])
        markup.row(InlineKeyboardButton(text=f"{brand['name']}", callback_data=f"blbrnd:{brand_id}"))
    return markup

# {'name': 'BSL350', 'id': '480', 'link': 'https://c.bm-corp.ru/mv/6b7da594-4880-4c0c-ac1f-0a6c3bf985d3'}

def models_keyboard(models: list, brand_id: int):
    markup = InlineKeyboardMarkup(row_width=2)
    for model in models:
        model_id = int(model['id'])
        markup.row(InlineKeyboardButton(text=f"{model['name']}", callback_data=f"blmdl:{brand_id}:{model_id}"))
    return markup

async def cheker_start(message: Message, state: FSMContext):
    customer = regCustomer(message.chat.id, message.chat.full_name)
    console.log(f"{customer.forLog} {arrow} {dict(msg=message.text)}")
    check = check_api_token(customer.token)
    if check == False:
        await message.answer("<em>💬  Токен не зарегистрирован в системе. Для добавления токена, нажмите /add_token</em>")
    else:
        text = f"{checker_title_text()}\n{checker_tips_text()}"
        is_dealer = customer.is_dealer()
        if is_dealer:
            crm_id = customer.data.crm_id
            check_permissions = getCheckWithoutCount(crm_id)
            print(check_permissions)
            if check_permissions == False:
                text = f"{checker_title_text()}\n{infoForDealer(customer.data.crm_id)}"
                await message.answer(text, reply_markup=main_menu())
            else:
                text = f"{checker_title_text()}\n{infoForDealer(customer.data.crm_id)}\n{checker_tips_text()}"
                await message.answer(text, reply_markup=checker_menu())
                await state.reset_state()
        else:
            await state.reset_state()
            await message.answer(text, reply_markup=checker_menu())

async def check_by_phone_dp(call: CallbackQuery, state: FSMContext):
    customer = regCustomer(call.message.chat.id, call.message.chat.full_name)
    console.log(f"{customer.forLog} {arrow} {dict(filter=call.data)}")
    await call.answer(cache_time=1)
    await call.message.edit_text(by_phone_text())
    await call.message.answer("<em>Ожидаю ввода номера...</em>", reply_markup=remove_keyboard())
    await CheckByPhone.InputNumber.set()


async def input_number_dp(message: Message, state: FSMContext):
    customer = regCustomer(message.chat.id, message.chat.full_name)
    console.log(f"{customer.forLog} {arrow} {dict(msg=message.text)}")
    try:
        print(int(message.text))
        phone_len = len(message.text)
        if int(phone_len) != 11:
            await message.answer("<em>💬 Номер телефона вводится в формате</em> <code>79990001122</code>\n\n<em>Ожидаю ввода номера...</em>", reply_markup=main_menu())
        else:
            # ### Запрос к апи
            phone = int(message.text)
            api_request = check_app_by_phone(customer.token, phone)
            if api_request:
                app = App(dCreated=api_request['dCreated'])
                date = app.dCreated.strftime('%d.%m.%Y года')
                await message.answer(f"<b>🔴 Данный номер телефона забронирован {date}</b>", reply_markup=main_menu())
                await state.reset_state()
                if customer.is_dealer():
                    getCheck(customer.data.crm_id)
            else:
                await message.answer("<b>🟢 Данный номер телефона отсутствует в базе клиентов</b>", reply_markup=main_menu())
                await state.reset_state()
                if customer.is_dealer():
                    getCheck(customer.data.crm_id)

    except:
        await message.answer("<em>💬 Номер телефона вводится в формате</em> <code>79990001122</code>\n\n<em>Ожидаю ввода номера...</em>", reply_markup=main_menu())
    # await message.answer("ответ сервера", reply_markup=main_menu())

async def check_by_name_dp(call: CallbackQuery, state: FSMContext):
    customer = regCustomer(call.message.chat.id, call.message.chat.full_name)
    console.log(f"{customer.forLog} {arrow} {dict(filter=call.data)}")
    token = customer.token
    await call.answer(cache_time=1, text="Выберите бренд")
    await call.message.edit_text(by_name_text())
    await call.message.answer(f"<em>Выбор бренда</em>", reply_markup=brands_menu(token))
    await CheckByName.InputBrand.set()

async def select_brand_dp(call: CallbackQuery, state: FSMContext):
    customer = regCustomer(call.message.chat.id, call.message.chat.full_name)
    brand_id = call.data.split(':')[1]
    console.log(f"{customer.forLog} {arrow} {dict(brand_id=brand_id)}")
    token = customer.token
    brand_name = get_brand(token, brand_id)
    async with state.proxy() as data:
        data['brand_id'] = brand_id
    await call.answer(cache_time=1, text="Выберите регион")
    await call.message.edit_text(f"<b>🏷 Бренд</b> {brand_name} ")
    await call.message.answer(f"<em>Выбор региона</em>", reply_markup=regions_menu(token))
    await CheckByName.InputRegion.set()

async def select_region_dp(call: CallbackQuery, state: FSMContext):
    customer = regCustomer(call.message.chat.id, call.message.chat.full_name)
    region_id = call.data.split(':')[1]
    token = customer.token
    region_name = get_region(token, region_id)
    async with state.proxy() as data:
        data['region_id'] = region_id
    console.log(f"{customer.forLog} {arrow} {dict(region_id=region_id)}")
    await call.answer(cache_time=1)
    await call.message.edit_text(f"<b>🏙 Регион</b> {region_name}")
    await call.message.answer(f"<em>💬Теперь напишите название компании для поиска</em>", reply_markup=main_menu())
    await CheckByName.InputName.set()
    # await state.reset_state()

async def input_name_dp(message: Message, state: FSMContext):
    customer = regCustomer(message.chat.id, message.chat.full_name)
    name_len = len(message.text)
    if name_len < 5:
        await message.answer(f"<em>💬 Минимальное количество символов для поиска - 5, введите еще раз...</em>")
    else:
        async with state.proxy() as data:
            brand_id = data['brand_id']
            region_id = data['region_id']
            name = message.text
            console.log(f"{customer.forLog} {arrow} {dict(name=name, region_id=region_id, brand_id = brand_id)}")
            api_request = check_app_by_name(customer.token, brand_id, region_id, name)
            if api_request:
                app = App(dCreated=api_request['dCreated'])
                date = app.dCreated.strftime('%d.%m.%Y года')
                await message.answer(f"<b>🔴 Данное название компании в этом регионе по выбранному бренду забронировано {date}</b>", reply_markup=main_menu())
                await state.reset_state()
                if customer.is_dealer():
                    getCheck(customer.data.crm_id)
            else:
                await message.answer("<b>🟢 Данное название компании отсутствует в базе клиентов</b>", reply_markup=main_menu())
                await state.reset_state()
                if customer.is_dealer():
                    getCheck(customer.data.crm_id)

async def brands_links_start(message: Message, state: FSMContext):
    customer = Customer.where('uid', message.chat.id).first()
    brands_list = get_brands_for_links(customer.token)
    await message.answer('Выберите бренд', reply_markup=brands_keyboard(brands_list))

async def show_brand_with_models(call: CallbackQuery, state: FSMContext):
    customer = Customer.where('uid', call.message.chat.id).first()
    brand_id = call.data.split(':')[1]
    models_list = get_models_by_brand_id(brand_id, customer.token)
    await call.message.edit_text('Выберите модель', reply_markup=models_keyboard(models_list, brand_id))

async def show_link_model(call: CallbackQuery, state: FSMContext):
    customer = Customer.where('uid', call.message.chat.id).first()
    brand_id = call.data.split(':')[1]
    model_id = call.data.split(':')[2]
    models_list = get_model_by_model_id(brand_id, model_id, customer.token)
    get_model_info = get_model_by_model_id(brand_id, model_id, customer.token)
    text = f"Ваша ссылка\n\n{get_model_info['link']}"
    await call.message.answer(text, disable_web_page_preview = False)



# DP
def register_checker(dp: Dispatcher):


    dp.register_message_handler(brands_links_start, text="Получить ссылку на модель", state="*")
    dp.register_callback_query_handler(
        show_brand_with_models, text_contains="blbrnd", state="*")
    dp.register_callback_query_handler(
        show_link_model, text_contains="blmdl", state="*")


    dp.register_message_handler(cheker_start, commands=["check"], state="*")
    dp.register_message_handler(
        cheker_start, text_contains="Проверка заявки", state="*")
    dp.register_callback_query_handler(
        check_by_phone_dp, text_contains="by_phone")
    dp.register_message_handler(
        input_number_dp, state=CheckByPhone.InputNumber)

    dp.register_callback_query_handler(
        check_by_name_dp, text_contains="by_name")
    dp.register_callback_query_handler(
        select_brand_dp, text_contains="brand", state=CheckByName.InputBrand)
    dp.register_callback_query_handler(
        select_region_dp, text_contains="r", state=CheckByName.InputRegion)
    dp.register_message_handler(
        input_name_dp, state=CheckByName.InputName)


