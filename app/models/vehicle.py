class Vehicle:
    def __init__(self, vehicle_id, avg_km_per_liter, license_plate, seats, fuel_tank_size, name, buy_date, sell_date,
                 purchase_value, sale_value, manufacturing_year):
        self.vehicle_id = vehicle_id
        self.avg_km_per_liter = avg_km_per_liter
        self.license_plate = license_plate
        self.seats = seats
        self.fuel_tank_size = fuel_tank_size
        self.name = name
        self.buy_date = buy_date
        self.sell_date = sell_date
        self.purchase_value = purchase_value
        self.sale_value = sale_value
        self.manufacturing_year = manufacturing_year

    @staticmethod
    def from_db_row(row):
        if row:
            return Vehicle(
                row[0],  # VehicleID
                row[1],  # AvgKmPerLiter
                row[2],  # LicensePlate
                row[3],  # Seats
                row[4],  # FuelTankSize
                row[5],  # Name
                row[6],  # BuyDate
                row[7],  # SellDate
                row[8],  # PurchaseValue
                row[9],  # SaleValue
                row[10]  # ManufacturingYear
            )
        return None

    def to_tuple(self):
        return (self.avg_km_per_liter, self.license_plate, self.seats, self.fuel_tank_size, self.name,
                self.buy_date, self.sell_date, self.purchase_value, self.sale_value, self.manufacturing_year)

    def __str__(self):
        return f"{self.name} (Placa: {self.license_plate}, Data Compra: {self.buy_date})"