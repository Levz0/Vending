class Malfunction:
    def __init__(self, employee, vendor, mal_type, report_date, resolution_date, reason):
        self.employee = employee
        self.vendor = vendor
        self.mal_type = mal_type
        self.report_date = report_date
        self.resolution_date = resolution_date
        self.reason = reason