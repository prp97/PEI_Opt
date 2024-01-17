import sqlite3

def load_models_id():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()

    q = ' SELECT ID_M FROM modelo '
    cursor.execute(q)

    models_id = []
    for id_ in cursor.fetchall():
        models_id.append(id_[0])

    return models_id


class Data:
    def __init__(self, model_id: int):
        self.model_id = model_id
        self.alpha = 0
        self.beta = 0
        self.delta = 0
        self.max_np = 0

        self.Cmax_out = dict()
        self.Cmax_in = dict()
        self.M = dict()
        self.np = dict()
        self.EP = []
        self.P = []
        self.EP_P = []
        self.EP_P_EP_P = []

        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()

        self.data = self.load_model()


    def load_model(self) -> dict:
        '''
        Cargar modelo desde la base de datos 
        Param: model_id: int identificador del modelo en a base de datos
        Return: diccionario con los parámetros de entrada del modelo
        '''

        ## modelo ##

        q = ' SELECT Alpha, Beta, Delta FROM Modelo WHERE ID_M=? '
        self.cursor.execute(q, (self.model_id, ))

        rows = self.cursor.fetchall()

        for row in rows:
            self.alpha = row[0]
            self.beta = row[1]
            self.delta = row[2]

        ## empresa-proceso ##

        q = ' SELECT ID_EP, ID_P, M, Cmax_out, Cmax_in FROM Empresa_Proceso WHERE ID_M=? '
        self.cursor.execute(q, (self.model_id, ))

        rows = self.cursor.fetchall()

        for row in rows:
            key = (row[0], row[1])

            self.EP_P.append(key)

            if row[0] not in self.EP:
                self.EP.append(row[0])
            if row[1] not in self.P:
                self.P.append(row[1])

            if row[0] not in self.np.keys():
                self.np[row[0]] = 1
            else:
                self.np[row[0]] += 1

            # M
            M_value = row[2]  
            self.M[key] = M_value

            # Cmax_out
            Cmax_out_value = row[3]  
            self.Cmax_out[key] = Cmax_out_value

            # Cmax_in
            Cmax_in_value = row[4] 
            self.Cmax_in[key] = Cmax_in_value

        for ep_p in self.EP_P:
            for ep_p_ in self.EP_P:
                if ep_p != ep_p_:
                    self.EP_P_EP_P.append(
                        (ep_p[0], ep_p[1], ep_p_[0], ep_p_[1]))

        data = {None: {
            'alpha': {None: self.alpha},
            'beta': {None: self.beta},
            'delta': {None: self.delta},
            'EP_P': {None: self.EP_P},
            'EP_P_EP_P': {None: self.EP_P_EP_P},
            'EP': {None: self.EP},
            'np': self.np,
            'P': {None: self.P},
            'M': self.M,
            'Cmax_out': self.Cmax_out,
            'Cmax_in': self.Cmax_in
        }}

        return data


    def insert_results(self, Fw_results, Fp_results, solver: str, transformation:str, solver_options:str, obj_val: float, termination_condition: str, solver_status: str, time: float):
        try:
            for item in Fw_results:
                self.insert_Fw_result(
                    item[0], item[1], solver, transformation, solver_options, round(Fw_results[item].value, 3))

            for item in Fp_results:
                self.insert_Fp_result(
                    item[0], item[1], item[2], item[3], solver, transformation, solver_options, round(Fp_results[item].value, 3))
                
            self.insert_solver_results(solver, transformation, solver_options, obj_val, termination_condition, solver_status, round(time, 3))

        except:
            pass


    def insert_solver_results(self, solver: str, transformation: str, solver_options: str, obj_val: float,  termination_condition: str, solver_status: str, time: float):
        try:
            self.cursor.execute('INSERT INTO Results_Info (ID_M, Solver, Transformation, Options, Total_Fw, Termination_Condition, Solver_Status, Time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (self.model_id, solver, transformation, solver_options, obj_val, termination_condition, solver_status, time))

            self.conn.commit()

        except:
            pass


    def insert_Fp_result(self, id_ep_1: int, id_p_1: int, id_ep_2: int, id_p_2: int, solver: str, transformation:str, solver_options:str, Fp: float):
        try:
            self.cursor.execute('INSERT INTO Fp_Results (ID_M, ID_EP1, ID_P1, ID_M2, ID_EP2, ID_P2, Solver, Transformation, Options, Fp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (self.model_id, id_ep_1, id_p_1, self.model_id, id_ep_2, id_p_2, solver, transformation, solver_options, Fp))

            self.conn.commit()

        except:
            pass


    def insert_Fw_result(self, id_ep: int, id_p: int, solver: str, transformation:str, solver_options:str, fw: float):   
        try:
            self.cursor.execute('INSERT INTO Fw_Results (ID_M, ID_EP, ID_P, Solver, Transformation, Options, Fw) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                (self.model_id, id_ep, id_p, solver, transformation, solver_options, fw))

            self.conn.commit()

        except:
            pass


    def close(self):
        self.cursor.close()
        self.conn.close()
