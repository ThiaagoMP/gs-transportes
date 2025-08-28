-- Criando a tabela Vehicle
CREATE TABLE IF NOT EXISTS Vehicle (
    VehicleID INTEGER PRIMARY KEY AUTOINCREMENT,
    AvgKmPerLiter REAL NOT NULL,
    LicensePlate VARCHAR(20) NOT NULL,
    Seats INTEGER NOT NULL,
    FuelTankSize INTEGER NOT NULL,
    Name VARCHAR(50) NOT NULL
);

-- Criando a tabela Driver
CREATE TABLE IF NOT EXISTS Driver (
    DriverID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(50) NOT NULL,
    Salary REAL NOT NULL,
    Contact VARCHAR(100) NOT NULL
);

-- Criando a tabela Route
CREATE TABLE IF NOT EXISTS Route (
    RouteID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    AvgKm REAL NOT NULL,
    Period VARCHAR(20) NOT NULL,
    AvgTimeMinutes INTEGER NOT NULL,
    Name VARCHAR(50) NOT NULL,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Student
CREATE TABLE IF NOT EXISTS Student (
    StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
    Contact VARCHAR(100) NOT NULL,
    Address VARCHAR(100) NOT NULL,
    Name VARCHAR(50) NOT NULL
);

-- Criando a tabela RouteStudent (tabela de relacionamento entre Route e Student)
CREATE TABLE IF NOT EXISTS RouteStudent (
    RouteID INTEGER,
    StudentID INTEGER,
    PRIMARY KEY (RouteID, StudentID),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- Criando a tabela StudentPayment
CREATE TABLE IF NOT EXISTS StudentPayment (
    StudentPaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER NOT NULL,
    Receipt BLOB,  -- Opcional (permite NULL)
    PaymentDate DATE NOT NULL,
    Amount REAL NOT NULL,
    Paid INTEGER NOT NULL,  -- Supondo que Paid é um booleano armazenado como INTEGER (0 ou 1) no SQLite
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);

-- Criando a tabela ExtraPayment
CREATE TABLE IF NOT EXISTS ExtraPayment (
    ExtraPaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    RouteID INTEGER NOT NULL,
    PaymentDate DATE NOT NULL,
    Amount REAL NOT NULL,
    Receipt BLOB,  -- Opcional (permite NULL)
    Description VARCHAR(255),  -- Opcional (permite NULL)
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID)
);

-- Criando a tabela Maintenance
CREATE TABLE IF NOT EXISTS Maintenance (
    MaintenanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    ServiceProvider VARCHAR(50) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,  -- Opcional (permite NULL)
    Description VARCHAR(255),  -- Opcional (permite NULL)
    Receipt BLOB,  -- Opcional (permite NULL)
    Amount REAL NOT NULL,
    Preventive INTEGER NOT NULL,  -- Supondo que Preventive é um booleano armazenado como INTEGER (0 ou 1)
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Refueling
CREATE TABLE IF NOT EXISTS Refueling (
    RefuelingID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    PricePerLiter REAL NOT NULL,
    Liters INTEGER NOT NULL,
    KmTraveled REAL NOT NULL,
    Description VARCHAR(255),  -- Opcional (permite NULL)
    RefuelingDate DATE NOT NULL,
    Receipt BLOB,  -- Opcional (permite NULL)
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela Trip
CREATE TABLE IF NOT EXISTS Trip (
    TripID INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleID INTEGER NOT NULL,
    AdditionalExpenses REAL NOT NULL,
    TotalKm REAL NOT NULL,
    PassengerFare REAL NOT NULL,
    PassengerCount INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,  -- Opcional (permite NULL)
    Description VARCHAR(255),  -- Opcional (permite NULL)
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Criando a tabela RouteDriver (tabela de relacionamento entre Route e Driver)
CREATE TABLE IF NOT EXISTS RouteDriver (
    RouteID INTEGER,
    DriverID INTEGER,
    PRIMARY KEY (RouteID, DriverID),
    FOREIGN KEY (RouteID) REFERENCES Route(RouteID),
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID)
);

-- Criando a tabela Bonus
CREATE TABLE IF NOT EXISTS Bonus (
    BonusID INTEGER PRIMARY KEY AUTOINCREMENT,
    DriverID INTEGER NOT NULL,
    Description VARCHAR(255),  -- Opcional (permite NULL)
    Receipt BLOB,  -- Opcional (permite NULL)
    BonusDate DATE NOT NULL,
    Amount REAL NOT NULL,
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID)
);