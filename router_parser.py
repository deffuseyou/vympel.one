import requests
import os
from config_reader import config_read


# TODO: добавить логирование

class Router:
    def __init__(self):
        self.__router_ip = config_read()['router-ip']
        self.__auth_token = os.environ['router_auth_token']

    def __login(self, ):
        r = requests.get(self.__router_ip + '/userRpm/LoginRpm.htm?Save=Save',
                         headers={'Referer': self.__router_ip + '/', 'Cookie': self.__auth_token})

        if r.status_code == 200:
            x = 1
            while x < 3:
                try:
                    session_id = r.text[r.text.index(self.__router_ip) + len(self.__router_ip) +
                                        1:r.text.index('userRpm') - 1]
                    return session_id
                except ValueError:
                    return 'Login error'
        else:
            return 'IP unreachable'

    def __logout(self, session_id):
        r = requests.get(self.__router_ip + '/' + session_id + '/userRpm/LogoutRpm.htm',
                         headers={'Referer': self.__router_ip + '/' + session_id + '/userRpm/MenuRpm.htm',
                                  'Cookie': self.__auth_token})
        if r.status_code == 200:
            return 'Loging out: ' + str(r.status_code)
        else:
            return 'Unable to logout'

    def get_dhcp_table(self, ):
        if self.__login() == 'IP unreachable' or self.__login() == 'Login error':
            return self.__login()

        else:
            session = self.__login()
        r = requests.get(
            self.__router_ip + '/' + session + '/userRpm/AssignedIpAddrListRpm.htm',
            headers={'Referer': self.__router_ip + '/' + session + '/userRpm/SysRebootRpm.htm',
                     'Cookie': self.__auth_token})
        rows = []
        for i in r.text.split('\n'):
            if i.startswith('"'):
                rows.append(i.split(', ')[1:3][::-1])
        return rows

    def get_mac_by_ip(self, ip):
        rows = self.get_dhcp_table()
        for client in rows:
            if client[0].replace('"', '') == ip:
                mac = client[1].replace('"', '')
                print(f'{ip} {mac}')
                return mac
