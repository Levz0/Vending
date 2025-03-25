class Lamp():
    def __init__(self, code, article, name, LampType, voltage, colorTemp, price, description):
        self.code = code
        self.article = article
        self.name = name
        self.type = LampType
        self.voltage = voltage
        self.colorTemp = colorTemp
        self.price = price
        self.description = description
        
    def  __str__(self):
        return self.name