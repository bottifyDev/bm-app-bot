from api import *

# token = "LOIMSYMPUY"

def get_brands_for_links(token):
  ex_data = get_models_data(token)
  ex_data_raw = ex_data.json()['data']['brands']
  result_list = [{'name': item['name'], 'id': item['id']} for item in ex_data_raw]
  return result_list

def get_models_by_id(id_to_find, token):
  ex_data = get_models_data(token)
  ex_data_raw = ex_data.json()['data']['brands']
  found_element = next((item for item in ex_data_raw if item['id'] == str(id_to_find)), None)
  if found_element:
    return found_element['models']
  else:
    return []

# print(get_models_by_id(37, "LOIMSYMPUY"))
# print(get_brands("LOIMSYMPUY"))