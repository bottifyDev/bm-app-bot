from rich.emoji import *
from orator import Model
from orator.orm import has_many
from orator.orm import belongs_to
from orator.orm import belongs_to_many
from orator.orm import scope
from orator.orm import accessor
from .connect import db

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
        return f"{uid} | {name}"






