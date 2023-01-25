import os
import asyncio
import logging

import time
from time import sleep
from rich.console import Console
from rich.status import *
from rich.spinner import *
from rich.progress import track
from rich.progress import Progress
from rich import print_json

from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.db import api
from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.auth import register_auth
from tgbot.handlers.checker import register_checker
from tgbot.handlers.echo import register_echo

from aiogram.dispatcher.webhook import configure_app
from aiohttp import web

from tgbot.db.models import *

logger = logging.getLogger(__name__)
console = Console(color_system="auto")

with console.status("[bold green]Запускаю бот...", spinner="moon", spinner_style="red") as status:
    sleep(3)



def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)

def register_all_handlers(dp):
    register_admin(dp)
    register_auth(dp)
    register_checker(dp)
    register_echo(dp)


config = load_config(".env")

storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=storage)

bot['config'] = config

async def on_startup(dispatcher) -> None:
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher) -> None:
    await bot.delete_webhook()


def main():


    console.rule("[bold blue] * ")
    console.log("===== Бот запущен! ======")
   

    register_all_filters(dp)
    register_all_handlers(dp)

    # handle /api route
    async def root_handler(request):
        return web.json_response({"status": "OK"}, status=200)

    async def api_handler(request):
        headers = request.headers
        try:
            auth = headers['Authorization']
            if auth == "kQYvSOG02hnbP8m6osI9xSZ5":
                dt = await request.json()
                text = dt['message']
                crm_token = dt['token']
                customers = Customer.where('token', '=', crm_token).get()
                if customers:
                    for customer in customers:
                        await bot.send_message(customer.uid, text)
                    print(dt)
                    return web.json_response({"status": "OK"}, status=200)
                else:
                    return web.json_response({"status": "user not found"}, status=404)
            else:
                return web.json_response({"status": "invalid auth token"}, status=401)
        except:
            return web.json_response({"status": "no auth token"}, status=401)

    app = web.Application()
    app.add_routes([web.get('/', root_handler)])
    app.add_routes([web.post('/', api_handler)])
    configure_app(dp, app, "/bot")
    
    web.run_app(app, port=8007)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")




