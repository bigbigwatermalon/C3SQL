import datetime

keys = {
    '3.1': False,
    '3.7': False,
    "3.8": False,
    '3.13': True,
}

def dprint(content, key=None):
    if key in keys.keys() and keys[key]:
        print('[' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ']', end=' ')
        print(content)

def dbool(key=None):
    if key in keys.keys() and keys[key]:
        return True
    return False
