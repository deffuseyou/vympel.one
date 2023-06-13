import os

from sqlighter import SQLighter

db = SQLighter(database='vympel.one',
               user='postgres',
               password=os.environ['ADMIN_PASSWORD'],
               host='192.168.0.100',
               port=5432).reset()
