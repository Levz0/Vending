class Vendor():
    def __init__(self, code, name, description):
        self.code = code
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"The vendor {self.name} is a {self.descriptiondesc}"
    
    