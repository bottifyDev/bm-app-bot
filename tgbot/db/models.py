import pytz
import pendulum
import datetime, time

from rich.emoji import *
from orator import Model
from orator.orm import has_one
from orator.orm import has_many
from orator.orm import belongs_to
from orator.orm import belongs_to_many
from orator.orm import scope
from orator.orm import accessor
from .connect import db

IST = pytz.timezone('Europe/Moscow')

class Customer(Model):
    __guarded__ = ['created_at', 'updated_at']
    __visible__ = ['id', 'name', 'uid', 'token', 'created_at']

    @accessor
    def summary(self):
        balance = self.balance
        register_date = self.created_at.diff_for_humans(locale="ru")
        you_name = f"\n\nВаше имя: <code>{self.name}</code>"
        you_register = f"\nРегистрация: <code>{register_date}</code>"
        you_balance = f"\nБаланс: <code>{balance}</code>"
        text = you_name + you_register + you_balance
        return text

    @accessor
    def forLog(self):
        uid = self.uid
        name = self.name
        data = self.data
        return f"{uid} | {name} {data.serialize()}"

    @has_one
    def data(self):
        return CustomersData

    def is_dealer(self):
        if int(self.data.category) == 100:
            return True
        else:
            return False

    def dealer_data(self):
            text = [
                '➖➖➖➖➖➖➖',
                f'<b>▪️ Период проверки:</b>',
            ]
            return "\n".join(text)


class CustomersData(Model):
    __guarded__ = ['created_at', 'updated_at']
    __visible__ = ['category', 'login', 'crm_id']

    @belongs_to
    def customer(self):
        return Customer

class Check(Model):
    __guarded__ = ['created_at', 'updated_at']

    def get_date(self):
        return self.updated_at.in_timezone('Europe/Moscow')

    def get_period(self):
        now = pendulum.now('Europe/Moscow')
        period = now - self.get_date()
        return period.seconds

    def get_last(self):
        now = pendulum.now('Europe/Moscow')
        period = now - self.get_date()
        return period

    def set_count(self):
        if int(self.count) >= 5:
            self.count = 1
            self.update()
        else:
            self.count = self.count + 1
            self.update()


class CheckConfig(Model):
    __table__ = 'check_config'
    __guarded__ = ['created_at', 'updated_at']

    def humanize(self):
        # p = pendulum.create().add(seconds=self.period)
        # days = int(p.strftime('%d')) - 10
        # hours = int(p.strftime('%H'))
        # minutes = int(p.strftime('%M'))
        # seconds = int(p.strftime('%S'))
        # return f"{days}д. {hours}ч. {minutes}мин. {seconds}сек."
        now = pendulum.now()
        add = now.add(seconds=self.period)
        period = add - now
        interval = period.as_interval()
        interval.set_locale('ru')
        return interval