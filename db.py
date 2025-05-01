import pymysql

class DataBase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
    
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )    
            
            self.cursor = self.connection.cursor()
            print("Подключение успешно!")
        except pymysql.MySQLError as err:
            print(f"Ошибка подключения: {err}")
            
    def closeConnection(self):
        if self.connection.open:
<<<<<<< HEAD
           self.connection.close()
           print("Соединение закрыто.")
=======
            self.connection.close()
            print("Соединение закрыто.")
>>>>>>> 80526ba0e9b5c1e7142da5ac125e973c8b1dac38
