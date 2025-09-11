import os
import sqlite3
import tkinter as tk
from repositories.vehicle_repository import VehicleRepository
from repositories.driver_repository import DriverRepository
from repositories.route_repository import RouteRepository
from repositories.student_repository import StudentRepository
from repositories.route_student_repository import RouteStudentRepository
from repositories.student_payment_repository import StudentPaymentRepository
from repositories.extra_payment_repository import ExtraPaymentRepository
from repositories.maintenance_repository import MaintenanceRepository
from repositories.refueling_repository import RefuelingRepository
from repositories.trip_repository import TripRepository
from repositories.trip_driver_repository import TripDriverRepository
from repositories.route_driver_repository import RouteDriverRepository
from repositories.bonus_repository import BonusRepository
from database import create_connection
from app.interface.interface import Interface


def initialize_database(db_file: str, sql_file: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório atual do script
    parent_dir = os.path.dirname(base_dir)  # Diretório pai
    db_path = os.path.join(parent_dir, 'database', 'data', os.path.basename(db_file))
    sql_path = os.path.join(parent_dir, 'database', 'scripts', sql_file)

    # Criar diretório database/data se não existir
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Conectar ao banco de dados
    conn = create_connection(db_path)
    if conn:
        try:
            cursor = conn.cursor()
            # Ler e executar o script SQL
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print(f"Banco de dados inicializado com sucesso em {db_path}")
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            print("Verifique o conteúdo do arquivo SQL para erros de sintaxe.")
        except FileNotFoundError:
            print(f"Arquivo SQL {sql_path} não encontrado")
        finally:
            conn.close()
    else:
        print("Falha ao conectar ao banco de dados")


def main():
    db_file = "gs_transportes.db"
    sql_file = "create_tables.sql"

    # Inicializar o banco de dados e criar tabelas
    initialize_database(db_file, sql_file)

    # Caminho do banco de dados para os repositórios
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    db_path = os.path.join(parent_dir, 'database', 'data', db_file)

    # Inicializando repositórios
    vehicle_repo = VehicleRepository(db_path)
    driver_repo = DriverRepository(db_path)
    route_repo = RouteRepository(db_path)
    student_repo = StudentRepository(db_path)
    route_student_repo = RouteStudentRepository(db_path)
    student_payment_repo = StudentPaymentRepository(db_path)
    extra_payment_repo = ExtraPaymentRepository(db_path)
    maintenance_repo = MaintenanceRepository(db_path)
    refueling_repo = RefuelingRepository(db_path)
    trip_repo = TripRepository(db_path)
    trip_driver_repo = TripDriverRepository(db_path)
    route_driver_repo = RouteDriverRepository(db_path)
    bonus_repo = BonusRepository(db_path)

    # Iniciar a interface gráfica
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()


if __name__ == "__main__":
    main()