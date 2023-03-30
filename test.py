import paramiko


host = '192.168.1.1'
user = 'root'
password = ''
port = 22

# Подключение к удаленному серверу
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=host, username=user, password=password, port=port)

# Открытие файла для дозаписи
sftp_client = ssh_client.open_sftp()
file = sftp_client.open('/etc/qwert.txt', 'a+')
file1 = sftp_client.open('/etc/qwert.txt', 'r')
print(file1.read().decode('utf-8').split('\n'))

# Запись данных в файл
file.write('192.168.0.191\n')

# Выполнение команды перезагрузки фаервола
ssh_client.exec_command('/etc/init.d/firewall restart')


# Закрытие файла и отключение от сервера
file.close()
sftp_client.close()
ssh_client.close()
