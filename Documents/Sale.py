class Sale:
    def __init__(self, code, vendor_usage, lamp, price, date):
        self.code = code                 # id продажи
        self.vendor_usage = vendor_usage # объект Vendor_usage или его строковое представление
        self.lamp = lamp                 # объект Lamp или его строковое представление
        self.price = price               # Цена
        self.date = date                 # Дата продажи

    def __str__(self):
        return f"Продажа {self.code}: {self.lamp} за {self.price} от {self.date}"