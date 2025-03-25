class Malfunction:
    def __init__(self, code, malfunction_type, vendor_usage, employee, status, reason, report_date, resolution_date):
        self.code = code
        self.malfunction_type = malfunction_type
        self.employee = employee
        self.status = status
        self.vendor_usage = vendor_usage
        self.reason = reason
        self.report_date = report_date
        self.resolution_date = resolution_date
    def __str__(self):
        return f"Неполадка № {self.code}"
        