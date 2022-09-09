from email import message
from typing import Optional
from unicodedata import category
import requests
import time
import datetime
from datetime import datetime, date
from pydantic import BaseModel


class App(BaseModel):
    dCreated: date

class Response(BaseModel):
    data: Optional[App]

auth_data = {"auth": "kQYvSOG02hnbP8m6osI9xSZ5"}

api_url = "https://company.bm-corp.ru/telegram/"


def compare_data(dt,token):
	dt['auth'] = "kQYvSOG02hnbP8m6osI9xSZ5"
	dt['token'] = token
	return dt

def compare_data_by_phone(dt,token,phone):
	dt['auth'] = "kQYvSOG02hnbP8m6osI9xSZ5"
	dt['token'] = token
	dt['filter[phone]'] = phone
	return dt

def compare_data_by_name(dt,token,brand_id, region_id, name):
	dt['auth'] = "kQYvSOG02hnbP8m6osI9xSZ5"
	dt['token'] = token
	dt['filter[brand]'] = brand_id
	dt['filter[region]'] = region_id
	dt['filter[name]'] = name
	return dt

def compare_data_for_brand(dt,token,brand_id):
	dt['auth'] = "kQYvSOG02hnbP8m6osI9xSZ5"
	dt['token'] = token
	dt['brand'] = brand_id
	return dt

def compare_data_for_region(dt,token,region_id):
	dt['auth'] = "kQYvSOG02hnbP8m6osI9xSZ5"
	dt['token'] = token
	dt['region'] = region_id
	return dt

def set_missing(dt,token):
	comparing_data = compare_data(dt,token)
	response = requests.post(api_url + "set_missing", data=comparing_data)
	return response

def get_reasons():
	response = requests.post(api_url + "get_reasons", data=auth_data)
	if response.json()['status'] == 1:
		return response.json()['data']
	else:
		return []

def get_reason(reason_id):
	reasons = get_reasons()
	res = {}
	for reason in reasons:
		if reason['id'] == str(reason_id):
			res['id'] = (reason['id'])
			res['name'] = (reason['name'])
	return res


def get_brands(token):
    dt = {}
    comparing_data = compare_data(dt, token)
    response = requests.post(api_url + "get_brands", data=comparing_data)
    try:
        if response.json()['status'] == 0:
            return response.json()['message']
        else:
            return response.json()['data']
    except:
        return False


def get_brand(token, brand_id):
    dt = {}
    comparing_data = compare_data_for_brand(dt, token, brand_id)
    response = requests.post(api_url + "get_brands", data=comparing_data)
    try:
        if response.json()['status'] == 0:
            return response.json()['message']
        else:
            return response.json()['data']['name']
    except:
        return False


def get_regions(token):
    dt = {}
    comparing_data = compare_data(dt, token)
    response = requests.post(api_url + "get_regions", data=comparing_data)
    try:
        if response.json()['status'] == 0:
            return response.json()['message']
        else:
            regions = response.json()['data']
            return regions

    except:
        return False


def get_region(token, region_id):
    dt = {}
    comparing_data = compare_data_for_region(dt, token, region_id)
    response = requests.post(api_url + "get_regions", data=comparing_data)
    try:
        return response.json()['data'][0]['name']
    except:
        return False


def check_app_by_phone(token, phone):
    dt = {}
    comparing_data = compare_data_by_phone(dt, token, phone)
    response = requests.post(api_url + "check_app", data=comparing_data)
    try:
        code = response.json()['status']
        if code == 0:
            data = []
        else:
            data = response.json()['data'][0]

        return data

    except Exception as e:
        return e

def check_app_by_name(token, brand, region, name):
    dt = {}
    comparing_data = compare_data_by_name(dt, token, brand, region, name)
    response = requests.post(api_url + "check_app", data=comparing_data)
    try:
        code = response.json()['status']
        if code == 0:
            data = []
        else:
            data = response.json()['data'][0]

        return data

    except Exception as e:
        return e

def check_api_token(token):
    dt = {}
    comparing_data = compare_data(dt, token)
    response = requests.post(api_url + "check_token", data=comparing_data)
    try:
        if response.json()['status'] == 0:
            return response.json()['message']
        else:
            if int(response.json()["data"][0]["tUser_categories"]) == 100:
                category = f"<b>▪️ Категория:</b> Дилер"
            else:
                category = f"<b>▪️ Категория:</b> Менеджер"
            text = [
                '➖➖➖➖➖➖➖',
                '<b>Ваши данные в CRM</b>',
                f'<b>▪️ Имя:</b> {response.json()["data"][0]["name"]}',
                f'<b>▪️ Фамилия:</b> {response.json()["data"][0]["fam"]}',
                f'<b>▪️ Логин:</b> {response.json()["data"][0]["login"]}',
                category
            ]
            return "\n".join(text)
    except:
        return False

def check_user(token):
    dt = {}
    comparing_data = compare_data(dt, token)
    response = requests.post(api_url + "check_token", data=comparing_data)
    try:
        if response.json()['status'] == 0:
            return dict(category=0, login=0, crm_id=0)
        else:
            category = response.json()['data'][0]['tUser_categories']
            login = response.json()['data'][0]['login']
            crm_id = response.json()['data'][0]['id']
            return dict(category=category, login=login, crm_id=crm_id)
    except:
        return False





