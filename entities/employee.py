class Employee():
    def __init__(self, FIO, post, birthDate, INN, phoneNumber, login, password):
        self.FIO = FIO
        self.post = post
        self.birthDate = birthDate
        self.INN = INN
        self.phoneNumber = phoneNumber
        self.login = login
        self.password = password
        
        print('Сотрудник инициализирован')
        
    def __str__(self):
        return f"Сотрудник {self.FIO} с должностью {self.post}"
         
