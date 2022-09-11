import requests
import os


def logout(session_id):
    router_ip = 'http://192.168.0.1'
    auth_token = os.environ['router_auth_token']

    r = requests.get(router_ip + '/' + session_id + '/userRpm/LogoutRpm.htm',
                     headers={'Referer': router_ip + '/' + session_id + '/userRpm/MenuRpm.htm', 'Cookie': auth_token})
    if r.status_code == 200:
        return 'Loging out: ' + str(r.status_code)
    else:
        return 'Unable to logout'


def login():
    router_ip = 'http://192.168.0.1'
    auth_token = os.environ['router_auth_token']

    r = requests.get(router_ip + '/userRpm/LoginRpm.htm?Save=Save',
                     headers={'Referer': router_ip + '/', 'Cookie': auth_token})

    if r.status_code == 200:
        x = 1
        while x < 3:
            try:
                session_id = r.text[r.text.index(router_ip) + len(router_ip) + 1:r.text.index('userRpm') - 1]
                return session_id
            except ValueError:
                return 'Login error'
    else:
        return 'IP unreachable'


def get_rpm_table():
    router_ip = 'http://192.168.0.1'
    auth_token = os.environ['router_auth_token']

    if login() == 'IP unreachable' or login() == 'Login error':
        return login()

    else:
        session = login()
    r = requests.get(
        router_ip + '/' + session + '/userRpm/AssignedIpAddrListRpm.htm',
        headers={'Referer': router_ip + '/' + session + '/userRpm/SysRebootRpm.htm', 'Cookie': auth_token})

    page = r.text
    m = []
    for i in page.split('\n'):
        if i.startswith('"'):
            m.append(i.split(', ')[1:3][::-1])
    return m


def get_mac_by_ip(ip):
    rpm_table = get_rpm_table()
    for client in rpm_table:
        if client[0].replace('"', '') == ip:
            mac = client[1].replace('"', '')
            print(f'{ip} {mac}')
            return mac
