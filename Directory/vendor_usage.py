from Directory.vendor import Vendor
class Vendor_usage():
    def __init__(self, code, vendor, install_date, location, status):
        self.code = code
        self.vendor = Vendor(vendor.code, vendor.name, vendor.description)
        self.install_date = install_date    
        self.location = location
        self.status = status
        
        
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        allowed_statuses = {'Активен', 'Неактивен', 'В обслуживании'}
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        self._status = value
        
    def __str__(self):
        return "Аппарат № " + str(self.code) + " " + str(self.vendor) + " " + str(self.location) + " "