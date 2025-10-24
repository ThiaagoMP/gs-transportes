import os
import sqlite3
import tkinter as tk

from app.database import create_connection
from app.repositories.route_extra_payment_repository import RouteExtraPaymentRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.route_student_repository import RouteStudentRepository
from app.repositories.student_payment_repository import StudentPaymentRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.refueling_repository import RefuelingRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.trip_driver_repository import TripDriverRepository
from app.repositories.route_driver_repository import RouteDriverRepository
from app.repositories.driver_bonus_repository import DriverBonusRepository
from app.interface.interface_principal import InterfacePrincipal

def initialize_database(db_file, sql_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    db_path = os.path.join(parent_dir, 'database', 'data', os.path.basename(db_file))
    sql_path = os.path.join(parent_dir, 'database', 'scripts', sql_file)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = create_connection(db_path)
    if conn:
        try:
            cursor = conn.cursor()
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print("Banco de dados inicializado com sucesso em {}".format(db_path))
        except sqlite3.Error as e:
            print("Erro ao inicializar o banco de dados: {}".format(e))
            print("Verifique o conteúdo do arquivo SQL para erros de sintaxe.")
        except FileNotFoundError:
            print("Arquivo SQL {} não encontrado".format(sql_path))
        finally:
            conn.close()
    else:
        print("Falha ao conectar ao banco de dados")


def main():
    db_file = "gs_transportes.db"
    sql_file = "create_tables.sql"

    initialize_database(db_file, sql_file)

    root = tk.Tk()
    app = InterfacePrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()
