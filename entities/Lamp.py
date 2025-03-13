class Lamp():
    def __init__(self, name, LampType, voltage, colorTemp, price, description):
        self.name = name
        self.type = LampType
        self.voltage = voltage
        self.colorTemp = colorTemp
        self.price = price
        self.description = description

        print('Лампа инициализирована')
        
    def  __str__(self):
        return f"Лампа {self.name} с вольтажем {self.voltage}"