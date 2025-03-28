class Location():
    def __init__(self, code, name, address):
        self.code = code
        self.name = name
        self.address = address
        
    def __str__(self):
        return self.name