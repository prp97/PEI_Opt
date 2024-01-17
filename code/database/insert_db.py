import sqlite3

# # Conectarse a la base de datos o crearla si no existe
# conn = sqlite3.connect('database.db')

# # Crear un cursor para ejecutar consultas
# cursor = conn.cursor()

# cursor.execute('INSERT INTO modelo (columna1, columna2, columna3) VALUES (?, ?, ?)',
#                ('valor1', 'valor2', 'valor3'))

def insert_Fpart_result(id_modelo: int, id_ep_1: int, id_p_1: int, id_ep_2: int, id_p_2: int, solver: str, fpart: float):
    '''
    Inserta en la base de datos los valores de las variables Fpart
    obtenidos al resolver un modelo de EIP con un solver específico

    :param id_modelo: id del modelo
    :param id_ep_1: id de la empresa que envía
    :param id_p_1: id del proceso que envía
    :param id_ep_2: id de la empresa que recibe
    :param id_p_2: id del proceso que recibe
    :param solver: solver empleado en la obtención del resultado
    :param fpart: valor obtenido por el solver
    '''    

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Fpart_result (ID_M, ID_EP1, ID_P1, ID_M2, ID_EP2, ID_P2, Solver, Fpart) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (id_modelo, id_ep_1, id_p_1, id_modelo, id_ep_2, id_p_2, solver, fpart))


def insert_Fw_result(id_modelo: int, id_ep: int, id_p: int, solver: str, fw: float):
    '''
    Inserta en la base de datos los valores de las variables Fw
    obtenidos al resolver un modelo de EIP con un solver específico

    :param id_modelo: id del modelo
    :param id_ep: id de la empresa que recibe
    :param id_p: id del proceso que recibe
    :param solver: solver empleado en la obtención del resultado
    :param fw: valor obtenido por el solver
    '''    

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Fw_results (ID_M, ID_EP, ID_P, Solver, Fw) VALUES (?, ?, ?, ?, ?)',
                   (id_modelo, id_ep, id_p, solver, fw))

    conn.commit()
