import requests
import os
import re
import string
from config_reader import config_read


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

    def whitelist_mac(self, mac_address):
        if self.__login() == 'IP unreachable' or self.__login() == 'Login error':
            return self.__login()

        else:
            session = self.__login()


        response = requests.get(self.__router_ip + '/' + session + '/userRpm/AccessCtrlHostsListsRpm.htm?addr_type=0&hosts_lists_name=imya_uzla_10&src_ip_start=&src_ip_end=&mac_addr=08-D8-C4-F2-76-E8&Changed=0&SelIndex=0&fromAdd=1&Page=1&Save=Сохранить',
                                headers={'Referer': self.__router_ip + '/' + session + '/userRpm/SysRebootRpm.htm',
                                         'Cookie': self.__auth_token}).text
        response3 = requests.get(self.__router_ip + '/' + session + '/userRpm/AccessCtrlAccessRulesRpm.htm?rule_name=imya_pravila_5&hosts_lists=8&targets_lists=255&scheds_lists=255&enable=1&Changed=0&SelIndex=0&Page=1&Save=Сохранить',
                                headers={'Referer': self.__router_ip + '/' + session + '/userRpm/SysRebootRpm.htm',
                                         'Cookie': self.__auth_token})
        return response


r = Router()
print(r.whitelist_mac('04-D4-C4-F2-76-E1'))
