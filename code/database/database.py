import sqlite3

# Conectarse a la base de datos o crearla si no existe
conn = sqlite3.connect('database/database.db')

# Crear un cursor para ejecutar consultas
cursor = conn.cursor()

# Modelo
cursor.execute(''' CREATE TABLE IF NOT EXISTS Modelo (
                        ID_M INTEGER PRIMARY KEY NOT NULL UNIQUE, 
                        Alpha REAL NOT NULL, 
                        Beta REAL NOT NULL, 
                        Delta REAL NOT NULL) ''')

# # Empresa_Proceso
cursor.execute(''' CREATE TABLE IF NOT EXISTS Empresa_Proceso (
                        ID_M INTEGER, 
                        ID_EP INTEGER NOT NULL, 
                        ID_P INTEGER NOT NULL, 
                        Cmax_in REAL, 
                        Cmax_out REAL,
                        M REAL, 
                        PRIMARY KEY(ID_M, ID_EP, ID_P), 
                        FOREIGN KEY(ID_M) REFERENCES Modelo(ID_M)) ''')

cursor.execute(''' CREATE TABLE IF NOT EXISTS Fw_Results (
                        ID_M INTEGER, 
                        ID_EP INTEGER NOT NULL, 
                        ID_P INTEGER NOT NULL, 
                        Solver STRING,
                        Transformation STRING,
                        Options STRING,
                        Fw REAL,
                        PRIMARY KEY(ID_M, ID_EP, ID_P, Solver),
                        FOREIGN KEY(ID_M) REFERENCES Modelo(ID_M)) ''')


cursor.execute(''' CREATE TABLE IF NOT EXISTS Fp_Results (
                        ID_M INTEGER,
                        ID_EP1 INTEGER, 
                        ID_P1 INTEGER, 
                        ID_M2 INTEGER,
                        ID_EP2 INTEGER, 
                        ID_P2 INTEGER, 
                        Solver STRING,
                        Transformation STRING,
                        Options STRING,
                        Fp REAL,
                        PRIMARY KEY(ID_M, Solver, Transformation, Options, ID_EP1, ID_P1, ID_EP2, ID_P2),
                        FOREIGN KEY(ID_M, ID_EP1, ID_P1) REFERENCES Empresa_Proceso(ID_M, ID_EP, ID_P),
                        FOREIGN KEY(ID_M2, ID_EP2, ID_P2) REFERENCES Empresa_Proceso(ID_M, ID_EP, ID_P),
                        CHECK (ID_M = ID_M2))''')


# results
cursor.execute(''' CREATE TABLE IF NOT EXISTS Results_Info (
                        ID_M INTEGER,
                        Solver STRING,
                        Transformation STRING,
                        Options STRING,
                        Total_Fw FLOAT, 
                        Termination_Condition STRING,
                        Solver_Status STRING,
                        Time FLOAT,
                        PRIMARY KEY(ID_M, Solver, Transformation, Options),
                        FOREIGN KEY(ID_M) REFERENCES Modelo(ID_M))''')

conn.commit()

conn.close()
