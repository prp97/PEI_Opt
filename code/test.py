import pandas as pd
from eip_model import *
from database.utils_db import *
from pyomo.environ import *

all_models_id = load_models_id()

solvers = [{'solver':'mpec_nlp', 'solver_options': '', 'transformation':''}, 
           {'solver': 'ipopt', 'solver_options': '', 'transformation' : 'mpec.standard_form'},
           {'solver': 'mpec_minlp', 'solver_options': '', 'transformation': ''}
           ]

rslt = []

for id_ in all_models_id:
    print('---------------- Modelo %s ----------------' % id_)

    list_obj_val= []
    list_term_cond = []
    list_solver = []
    list_time = []

    for item in solvers:
        solver = item['solver'] 
        transformation = item['transformation']
        solver_options = item['solver_options']

        print('*** Solver %s ' % solver, 'Transformación %s ' % transformation, 'Opciones %s ' % solver_options, ' ***')

        data = Data(id_)

        instance = model(id_, data)
        # instance.pprint()
        
        try:
            obj_value, termination_condition, solver_status, time = solve(instance, solver, transformation, solver_options)
            
            rslt.append({'Model': id_, 'Solver': f'{solver}_{transformation}', 'Objective Value': obj_value, 'Termination Condition': termination_condition, 'Time': time})
            
            evaluate(instance, solver + '_' + transformation) # guardar resultados en .csv

            data.insert_results(instance.Fw, instance.Fp, solver, transformation, solver_options, obj_value, termination_condition, solver_status, time)

            data.close()
        
        except:
            print()
            print('Error applying ', solver, transformation, solver_options, 'on model ', id_)
            print()


df = pd.DataFrame(rslt)
df.to_csv(f'data_csv/results_data.csv', index=False)
print(df)