from tabnanny import check
import pendulum
from locale import currency
from .models import *
from rich import pretty
from rich.emoji import *
from rich.console import Console
from api import check_user
from .connect import db

console = Console(color_system="256")
arrow = Emoji('arrow_right')
pretty.install()

def setCheckConfig(period):
    config = CheckConfig.all().first()
    config.period = period
    config.save()
    updateCounts()
    return config.serialize()

def setCheck(crm_id):
    # Создаем проверку для юзера crm если еще не
    check = Check.first_or_create(crm_id=crm_id)
    return check

def getCheck(crm_id):
    #
    period = CheckConfig.first().period
    first_or_create = setCheck(crm_id)
    check = Check.where('crm_id', crm_id).first()
    if check.get_period() < int(period) and check.count < 5:
        check.set_count()

    elif check.get_period() >= int(period) and check.count == 5:
        check.count = 0
        check.update()

    elif check.get_period() > int(period) and check.count < 5:
        check.set_count()

    elif check.get_period() < int(period) and check.count == 5:
        return False


def getCheckWithoutCount(crm_id):
    period = CheckConfig.first().period
    first_or_create = setCheck(crm_id)
    check = Check.where('crm_id', crm_id).first()
    if check.get_period() < int(period) and check.count == 5:
        return False
    elif check.get_period() >= int(period):
        check.count = 0
        check.update()
        return dict(count=check.count)
    else:
        return dict(count=check.count)

def infoForDealer(crm_id):
    current_period = CheckConfig.first().humanize()
    if getCheckWithoutCount(crm_id):
        if Check.where('crm_id', crm_id).first().count == 5:
            current_count = 0
            future_date_text = f"-"
            last_date = f"----"
        else:
            current_count = Check.where('crm_id', crm_id).first().count
            future_date_text = f"-"
            if current_count == 0:
                last_date = f"-"
            else:
                last_date = Check.where('crm_id', crm_id).first().get_date().strftime("%d.%m.%y - %H:%M:%S")
    else:
        current_count = Check.where('crm_id', crm_id).first().count
        current_date = Check.where('crm_id', crm_id).first().get_date()
        seconds = int(CheckConfig.first().period)
        now = pendulum.now('Europe/Moscow')
        future_date = current_date.add(seconds=seconds)
        period = future_date - now
        interval = period.as_interval()
        interval.set_locale('ru')
        future_date_str = future_date.strftime("%d.%m.%y - %H:%M:%S")
        future_date_text = f"\n<em>⏳ Проверка будет доступна через\n{interval}</em>"
        last_date = Check.where('crm_id', crm_id).first().get_date().strftime("%d.%m.%y - %H:%M:%S")
    text = [
        '➖➖➖➖➖➖➖',
        f'<b>▪️ Период проверки: {current_period}</b>',
        f'<b>▪️ Использовано проверок: {current_count}/5</b>',
        # f'<b>▪️ Последняя проверка: {last_date}</b>',
        future_date_text
        ]
    return "\n".join(text)


def delCheck(crm_id):
    check = Check.where('crm_id', crm_id).first()
    check.delete()
    return True

def updateCounts():
    Check.where('count', '>', 0).update(count=0)

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
        customer_data = CustomersData()
        customer_data.customer_id = customer.id
        customer_data.category = 0
        customer_data.login = "-"
        customer_data.crm_id = 0
        customer_data.save()
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




