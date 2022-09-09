from locale import currency
from .models import *
from rich import pretty
from rich.emoji import *
from rich.console import Console
from api import check_user

console = Console(color_system="256")
arrow = Emoji('arrow_right')
pretty.install()

def getInformation():
    """Получение статистики
    """
    customers_count = Customer.all().count()
    return f"<b>👥 Пользователей в боте:</b> {customers_count}"

def findCustomer(uid):
    """Поиск пользователя по telegram id
       Возвращает обьект customer
    """
    customer = Customer.where('uid', str(uid)).first()
    return customer

def regCustomer(uid,name):
    """Регистрация пользователя(если еще нет)
       Возвращает обьект customer
    """
    customer = Customer.where('uid', str(uid)).first()
    if customer:
        if customer.data:
            from_api = check_user(customer.token)
            try:
                customer.data.category = from_api['category']
                customer.data.crm_id = from_api['crm_id']
                customer.data.login = from_api['login']
                customer.data.save()
            except:
                pass
        else:
            check = check_user(customer.token)
            if check:
                customer_data = CustomersData()
                customer_data.customer_id = customer.id
                customer_data.category = check['category']
                customer_data.login = check['login']
                customer_data.crm_id = check['crm_id']
                customer_data.save()
        return customer
    else:
        customer = Customer.create(
            uid=uid,
            name=name,
            balance=0,
            token=123)
        return customer


def getCustomers(banned=0):
    """Получение пользователей
    Аргументы:
        banned {number} -- 1 или 0 (default: {0})
    Возвращает:
        list -- json список всех пользователей
    """
    customers = Customer.where('banned', banned).get().serialize()
    return customers

def getCustomer(customer_id):
    """Получение пользователя по id
    Возвращает обьект customer
    """
    customer = Customer.find(customer_id).serialize()
    return customer

def getToken(uid):
    """ Проверка на наличие токена
    """
    customer = findCustomer(uid)
    if customer.token == None:
        return "0"
    else:
        return customer.token

def addToken(uid, token):
    """ Добавление/смена токена
    """
    customer = findCustomer(uid)
    customer.update(token=token)
    return token

def banCustomer(customer_id):
    q = Customer.find(customer_id)
    return q.ban()

def updateCustomer(customer_id: int, params):
    customer = Customer.find(customer_id)
    if customer:
        customer.update(params)
        return customer.serialize()
    else:
        return "customer not found"




