-- Criando a tabela Vehicle
CREATE TABLE IF NOT EXISTS Vehicle (
    VehicleID INTEGER PRIMARY KEY,
    AvgKmPerLiter REAL NOT NULL,
    LicensePlate VARCHAR(20) NOT NULL,
    Seats INTEGER NOT NULL,
    FuelTankSize INTEGER NOT NULL,
    Name VARCHAR(50) NOT NULL,
    BuyDate DATE,
    SellDate DATE,
    PurchaseValue REAL NOT NULL,
    SaleValue REAL,
    ManufacturingYear INTEGER NOT NULL
);

-- Criando a tabela Driver
CREATE TABLE IF NOT EXISTS Driver (
    DriverID INTEGER PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Salary REAL NOT NULL,
    Contact VARCHAR(100) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    CPF VARCHAR(14) NOT NULL,
    RG VARCHAR(20) NOT NULL,
    CNH VARCHAR(20) NOT NULL,
    ExtraInfo VARCHAR(255)
);

-- Criando a tabela Route
CREATE TABLE IF NOT EXISTS Route (
    RouteID INTEGER PRIMARY KEY,
    VehicleID INTEGER NOT NULL,
    AvgKm REAL NOT NULL,
    Period VARCHAR(20) NOT NULL,
    AvgTimeMinutes INTEGER NOT NULL,
    Name VARCHAR(50) NOT NULL,
    ACTIVE SMALLINT NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Student
CREATE TABLE IF NOT EXISTS Student (
    StudentID INTEGER PRIMARY KEY,
    Contact VARCHAR(100) NOT NULL,
    Address VARCHAR(100) NOT NULL,
    Name VARCHAR(50) NOT NULL,
    ExtraInfo VARCHAR(255),
    ContractValue REAL NOT NULL,
    DueDay INTEGER NOT NULL,
    RG VARCHAR(20) NOT NULL,
    CPF VARCHAR(14) NOT NULL
);

-- Criando a tabela RouteStudent
CREATE TABLE IF NOT EXISTS RouteStudent (
    RouteID INTEGER,
    StudentID INTEGER,
    StartDate DATE NOT NULL,
    EndDate DATE,
    PRIMARY KEY (RouteID, StudentID),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- Criando a tabela StudentPayment
CREATE TABLE IF NOT EXISTS StudentPayment (
    StudentPaymentID INTEGER PRIMARY KEY,
    StudentID INTEGER NOT NULL,
    Receipt BLOB,
    PaymentDate DATE NOT NULL,
    Amount REAL NOT NULL,
    Paid SMALLINT NOT NULL,
    ExtraInfo VARCHAR(255),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- Criando a tabela ExtraPayment
CREATE TABLE IF NOT EXISTS RouteExtraPayment (
    ExtraPaymentID INTEGER PRIMARY KEY,
    RouteID INTEGER NOT NULL,
    PaymentDate DATE NOT NULL,
    Amount REAL NOT NULL,
    Receipt BLOB,
    Description VARCHAR(255),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID)
);

CREATE TABLE IF NOT EXISTS RouteExpensePayment (
    ExpensePaymentID INTEGER PRIMARY KEY,
    RouteID INTEGER NOT NULL,
    PaymentDate DATE NOT NULL,
    Amount REAL NOT NULL,
    Receipt BLOB,
    Description VARCHAR(255),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID)
);

-- Criando a tabela Maintenance
CREATE TABLE IF NOT EXISTS Maintenance (
    MaintenanceID INTEGER PRIMARY KEY,
    VehicleID INTEGER NOT NULL,
    ServiceProvider VARCHAR(50) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Description VARCHAR(255),
    Receipt BLOB,
    Amount REAL NOT NULL,
    Preventive INTEGER NOT NULL,
    MileageAtService INTEGER NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Refueling
CREATE TABLE IF NOT EXISTS Refueling (
    RefuelingID INTEGER PRIMARY KEY,
    VehicleID INTEGER NOT NULL,
    PricePerLiter REAL NOT NULL,
    Liters INTEGER NOT NULL,
    KmTraveled REAL NOT NULL,
    Description VARCHAR(255),
    RefuelingDate DATE NOT NULL,
    FuelType VARCHAR(20) NOT NULL,
    Receipt BLOB,
    GasStation VARCHAR(50) NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Trip
CREATE TABLE IF NOT EXISTS Trip (
    TripID INTEGER PRIMARY KEY,
    VehicleID INTEGER NOT NULL,
    AdditionalExpenses REAL NOT NULL,
    TotalKm REAL NOT NULL,
    PassengerFare REAL NOT NULL,
    PassengerCount INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Description VARCHAR(255),
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

CREATE TABLE IF NOT EXISTS TripDriver (
    TripID INTEGER,
    DriverID INTEGER,
    PRIMARY KEY (TripID, DriverID),
    FOREIGN KEY (TripID) REFERENCES Trip(TripID),
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID)
);

-- Criando a tabela RouteDriver
CREATE TABLE IF NOT EXISTS RouteDriver (
    RouteID INTEGER,
    DriverID INTEGER,
    PRIMARY KEY (RouteID, DriverID),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID),
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID)
);

-- Criando a tabela Bonus
CREATE TABLE IF NOT EXISTS DriverBonus (
    BonusID INTEGER PRIMARY KEY,
    DriverID INTEGER NOT NULL,
    Description VARCHAR(255),
    Receipt BLOB,
    BonusDate DATE NOT NULL,
    Amount REAL NOT NULL,
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID)
);