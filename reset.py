from sqlighter import SQLighter
import os

db = SQLighter(database='vympel.one',
               user='postgres',
               password=os.environ['admin_password'],
               host='192.168.0.100',
               port=5432).reset()
