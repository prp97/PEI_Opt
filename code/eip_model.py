from pyomo.environ import *

from pyomo.mpec import *
from pyomo.util.model_size import build_model_size_report

from rules import *

from database.utils_db import Data

from pyomo.common.timing import TicTocTimer, report_timing

import pandas as pd


def model(model_id: int, param_data: Data) -> AbstractModel:
    '''
    Crea una instancia de un modelo abstracto de pyomo.
    Añade como restricciones del estado (líder) los sistemas KKT concatenados de todas las empresas

    :param model_id: identificador del modelo
    :param param_data: instancia de la clase Data que contiene los parámetros de entrada para crear el modelo
    :return: instancia de un modelo abstracto de pyomo
    '''

    model_name = 'EIP_%s' % str(model_id)
    data_db = param_data

    # Crear un modelo abstracto de pyomo
    model = AbstractModel(name=model_name)

    # Conjuntos de entrada #

    # Conjunto de índices para las variables  
    model.EP_P = Set(dimen=2, ordered=Set.SortedOrder)  # Tuplas (ep, p)
    model.EP_P_EP_P = Set(dimen=4, ordered=Set.SortedOrder)  # Tuplas (ep, p, ep', p')

    # Conjunto de índices de las restricciones de desigualdad C = {1, 4}
    model.C = Set(within=NonNegativeReals, initialize=[1, 4])

    ##

    # Parámetros de entrada #

    # Concentración máxima de contaminantes permitida en la salida de los procesos
    model.Cmax_out = Param(model.EP_P, mutable=True)
    # Concentración máxima de contaminantes permitida en la entrada de los procesos
    model.Cmax_in = Param(model.EP_P, mutable=True)
    model.M = Param(model.EP_P, mutable=True)  # Carga contaminante

    model.alpha = Param(mutable=True)  # Precio de compra del agua dulce
    model.beta = Param(mutable=True)  # Costo de descarga de agua contaminada
    model.delta = Param(mutable=True)  # Costo de bombeo de agua contaminada

    ##

    # Variables #

    # Flujo de agua dulce al proceso de una empresa
    model.Fw = Var(model.EP_P, within=NonNegativeReals, rule=fw_rule)

    # Flujo de agua entre procesos
    model.Fp = Var(model.EP_P_EP_P, within=NonNegativeReals, rule=fp_rule)

    # Multiplicadores #

    # multiplicador asociado a la restricción r-ésima (r={1, 4}) del proceso p en la empresa ep
    model.mu = Var(model.EP_P, model.C, within=NonNegativeReals, rule=mu_rule)
    
    # multiplicador asociado a la restriccion 2 de
    model.mu_2 = Var(model.EP_P_EP_P, within=NonNegativeReals, rule=mu_2_rule)
    
    # multplicador asociado a la restricción de igualdad para la empresa ep en el proceso p
    model.lmbd = Var(model.EP_P, within=Reals, rule=lmbd_rule)

    ##

    # Nivel Superior #

    # Añadir la función objetivo del nivelsuperior (estado) al modelo
    model.upper_level_objective = Objective(
        rule=upper_level_objective_rule, sense=minimize
    )

    # Restricción del problema del nivel superior
    # No negatividad del flujo de agua fresca
    # Fw >= 0
    model.upper_level_constraint = Constraint(
        model.EP_P, rule=upper_level_constraint_rule
    )

    ##

    # Nivel Inferior #

    # Función objetivo del nivel inferior #

    # model.lower_level_objective = Objective(
    #     model.EP, rule=lower_level_objective_rule, sense=minimize)

    ##

    # Primera restricción del nivel inferior (Desigualdad) #
    # Concentración de contaminante permitida en entrada/salida de un proceso #
    model.constraint_1 = Constraint(model.EP_P, rule=lower_level_constraint_1_rule)

    ##

    # Segunda restricción del nivel inferior (Desigualdad) #
    # Fp >= 0 #
    model.constraint_2 = Constraint(model.EP_P_EP_P, rule=lower_level_constraint_2_rule)

    # ##

    # Tercera restricción del nivel inferior (Igualdad) #
    # Balance ... #
    model.constraint_3 = Constraint(model.EP_P, rule=lower_level_constraint_3_rule)

    # ##

    # Cuarta restricción del nivel inferior (Desigualdad) #
    # Cantidad de agua que recibe es mayor que la cantidad que envía #
    model.constraint_4 = Constraint(model.EP_P, rule=lower_level_constraint_4_rule)

    # ##

    # Restricciones para multiplicadores #

    model.mu_constraint = Constraint(model.EP_P, model.C, rule=mu_constraint_rule)

    model.mu_2_constraint = Constraint(model.EP_P_EP_P, rule=mu_2_constraint_rule)

    # ##

    # Restricciones de complementariedad para la primera y cuarta restricción #

    model.complementarity = Complementarity(
        model.EP_P, model.C, rule=complementarity_rule)

    # ##

    # # Restricciones de complementariedad para la segunda restricción #

    model.complementarity_2 = Complementarity(
        model.EP_P_EP_P, rule=complementarity_2_rule)

    # ##
    model.lagrangian = Constraint(model.EP_P_EP_P, rule=lagrangian_expr)

    instance = model.create_instance(data_db.data, name=model_name)

    # report_timing() # reportar tiempo de construcción del modelo

    return instance


def print_instance(instance) -> None:
    '''
    Imprime un modelo de pyomo

    :param instance: modelo de pyomo
    '''

    instance.pprint() 


def solve(instance, solver: str, transformation='', options=''):
    '''
    Resuelve el modelo con el solver indicado

    :param instance: instancia de un modelo abstracto de pyomo
    :param solver: nombre del solver a utilizar
    '''

    if transformation != '':
        TransformationFactory(transformation).apply_to(instance) # type: ignore

    opt = SolverFactory(solver, load_solutions=True, tee=True, report_timing=True)

    # if solver == 'mpec_nlp':
    #     opt.options['mpec_bound'] = 0.1 

    results = opt.solve(instance)

    # results.write() # imprimir los resultados del solver

    obj_value = round(value(instance.upper_level_objective), 3) # type: ignore

    try:
        # instance.display()
        return obj_value, results.solver.termination_condition, results.solver.status, results.solver.time
    
    except:
        return obj_value, results.solver.termination_condition, results.solver.status, results.solver.wallclock_time

def evaluate(model, solver):
    max_val_equal = 0    
    max_val_ineq_g = 0    
    max_val_ineq_l = 0

    re = []
    r1 = []
    r2 = []
    r3 = []
    r4 = []
    lg = []
    comp = []
    comp_2 = []
    mu = []
    mu_2 = []

    for item in model.EP_P:
        val = value(model.upper_level_constraint[item].body)
        
        val = round(val, 3) # type: ignore
        re.append(['Rest_est', item, val, val >= 0])

        ### 

        val = value(model.constraint_1[item].body)
        
        val = round(val, 3) # type: ignore
        r1.append(['R1', item, val, val <= 0])

        val_1 = round(value(model.mu[item, 1])) # type: ignore
        mu.append(['mu', item, val_1, val_1 >= 0])
        comp.append(['comp_1', item, val*val_1, val*val_1 == 0])

        ###

        val = value(model.constraint_3[item].body)

        val = round(val, 3) # type: ignore
        r3.append(['R3', item, val, val == 0])

        ###

        val = value(model.constraint_4[item].body)
        
        val = round(val , 3) # type: ignore
        r4.append(['R4', item, val, val <= 0]) 
        
        val_1 = round(value(model.mu[item, 4])) # type: ignore
        mu.append(['mu', item, val_1, val_1 >= 0])
        comp.append(['comp_4', item, val*val_1, val*val_1 == 0])

        ###

    for item in model.EP_P_EP_P:
        val = value(model.constraint_2[item].body)
                
        val = round(val, 3) # type: ignore
        r2.append(['R2', item, val, val >= 0])
        
        val_1 = round(value(model.mu_2[item])) # type: ignore
        mu.append(['mu_2', item, val_1, val_1 >= 0])
        comp_2.append(['comp_2', item, val*val_1, val*val_1 == 0])

        ###

        val = value(model.lagrangian[item].body) 
                
        val = round(val, 3) # type: ignore             
        lg.append(['Lg', item, val, val == 0])

    re.extend(r1)
    re.extend(r2)
    re.extend(r3)
    re.extend(r4)
    re.extend(lg)
    re.extend(comp)
    re.extend(comp_2)
    re.extend(mu)
    re.extend(mu_2)

    df = pd.DataFrame(re, columns=['Restr', 'Index', 'Valor', 'Se cumple'])
    df.to_csv(f'data_csv/data_{model.name}_solver_{solver}.csv', index=False)
    df.name = f'data_{model.name}_solver_{solver}'

    # print(df.name)
    # print(df)
    
    