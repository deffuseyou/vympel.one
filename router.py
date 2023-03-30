import paramiko
from config_reader import config_read


def add_ip(ip_address):
    config = config_read()
    # Подключение к удаленному серверу
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=config['router']['ip'],
                       username=config['router']['user'],
                       password=config['router']['password'])

    # Открытие файла для дозаписи
    sftp_client = ssh_client.open_sftp()
    with sftp_client.open(config['whitelist-path'], 'a+') as file:
        # Запись данных в файл
        file.write(f'{ip_address}\n')
        # Выполнение команды перезагрузки фаервола
        ssh_client.exec_command('/etc/init.d/firewall restart')

    # Копирование содержимого в локальный файл
    with sftp_client.open(config['whitelist-path'], 'r') as file:
        content = file.read().decode('utf-8').split('\n')
        print(content)

    # Отключение от сервера
    sftp_client.close()
    ssh_client.close()


if __name__ == "__main__":
    add_ip('192.168.0.100')
