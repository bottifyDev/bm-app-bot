from api import *
from tgbot.db.api import *

def clear_duble(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

res = []
for user in Customer.all():
    if len(user.token) > 3:
        res.append(user.token)
remove_d = clear_duble(res)

dillers = []

for token in remove_d:
    check = check_user(token)
    if check['category'] != '100':
        ids = []
        users = Customer.where('token', '=', token).get()
        for user in users:
            ids.append(user.uid)
        dct = dict(login=check['login'], crm_id=check['crm_id'], token=token, ids=ids)
        dillers.append(dct)

print(dillers)






