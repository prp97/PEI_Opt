from pyomo.environ import *

from pyomo.mpec import *
from pyomo.core.expr.calculus.derivatives import differentiate


def fw_rule(model, ep, p):
    '''
    Define el valor de inicialización de la variable Fw en el modelo

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: valor de inicialización
    '''    

    return model.M[ep, p] / model.Cmax_out[ep,p]


def fp_rule(model, ep, p, ep_, p_):
    '''
    Define el valor de inicialización de la variable Fp en el modelo

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: 0
    '''  

    return 0


def mu_2_rule(model, ep, p, ep_, p_):
    '''
    Define el valor de inicialización de la variable mu_2 en el modelo

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: 0
    '''    

    return 0


def lmbd_rule(model, ep, p): 
    '''
    Define el valor de inicialización de la variable lmbd en el modelo

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: 0
    '''    

    return 0


def mu_rule(model, ep, p, c):
    '''
    Define el valor de inicialización de la variable mu en el modelo

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: 0
    '''    

    return 0


def upper_level_objective_rule(model):
    '''
    Define la objetivo del estado (líder / nivel superior del problema de dos niveles)

    :param model: instancia de un modelo abstracto
    :return: expresión de la función objetivo
    '''

    return sum(
        model.Fw[ep, p] for ep, p in model.EP_P
    )  


def upper_level_constraint_rule(model, ep, p):
    '''
    Define la restricción del problema del estado, la cantidad de agua fresca que
    le da a cada proceso de cada empresa es no negativa

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: expresión de la restricción
    '''

    return model.Fw[ep, p] >= 0


def lower_level_objective_rule(model, ep):
    '''
    Función objetivo de cada empresa (seguidor / nivel inferior del problema de dos niveles)

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :return: expresión de la función objetivo
    '''

    return (
        model.alpha.value * sum(model.Fw[ep, p] for ep1, p in model.EP_P if ep == ep1)
        + model.beta.value
        * sum(
            model.Fw[ep, p]
            + (
                sum(
                    model.Fp[ep_, p_, ep, p]
                    for ep_, p_ in model.EP_P
                    if (ep, p) != (ep_, p_)
                )
            )
            - (
                sum(
                    model.Fp[ep, p, ep_, p_]
                    for ep_, p_ in model.EP_P
                    if (ep, p) != (ep_, p_)
                )
            )
            for ep1, p in model.EP_P
            if ep == ep1
        )
        + model.delta.value
        * (
            sum(
                model.Fp[ep, p, ep, p_]
                for ep1, p in model.EP_P
                if ep == ep1
                for ep2, p_ in model.EP_P
                if ep == ep2
                if p != p_
            )
        )
        + model.delta.value
        / 2
        * (
            sum(
                (model.Fp[ep, p, ep_, p_] + model.Fp[ep_, p_, ep, p])
                for ep_, p_ in model.EP_P
                for ep1, p in model.EP_P
                if ep == ep1 and ep != ep_
            )
        )
    )


def lower_level_constraint_1(model, ep, p):
    '''
    Expresión de la primera restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: expresión de la restricción
    '''

    return sum(
        model.Cmax_out[ep_, p_] * model.Fp[ep_, p_, ep, p]
        for ep_, p_ in model.EP_P
        if (ep, p) != (ep_, p_)
    ) - model.Cmax_in[ep, p] * (
        model.Fw[ep, p]
        + sum(
            model.Fp[ep_, p_, ep, p]
            for ep_, p_ in model.EP_P
            if (ep, p) != (ep_, p_)
        )
    )


def lower_level_constraint_1_rule(model, ep, p):
    '''
    Regla para añadir la primera restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: restricción
    '''

    return lower_level_constraint_1(model, ep, p) <= 0


def lower_level_constraint_2(model, ep, p, ep_, p_):
    '''
    Expresión de la segunda restricción del problema de una empresa con respecto a uno de
    sus procesos y el resto de los procesos de las demás empresas (puede ser la misma empresa).
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: expresión de la restricción
    '''

    return model.Fp[ep, p, ep_, p_]


def lower_level_constraint_2_rule(model, ep, p, ep_, p_):
    '''
    Regla para añadir la segunda restricción del problema de una empresa con respecto a uno de
    sus procesos y el resto de los procesos de las demás empresas (puede ser la misma empresa).
    La cantidad de agua que le da un proceso de una empresa a otro proceso (puede ser de la misma empresa) es no negativa (Fp >= 0).
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: restricción
    '''

    return lower_level_constraint_2(model, ep, p, ep_, p_) >= 0


def lower_level_constraint_3(model, ep, p):
    '''
    Expresión de la tercera restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de igualdad.

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: expresión de la restricción
    '''

    return (
        model.M[ep, p]
        + sum(
            model.Cmax_out[ep_, p_] * model.Fp[ep_, p_, ep, p]
            for ep_, p_ in model.EP_P
            if (ep, p) != (ep_, p_)
        )
        - model.Cmax_out[ep, p]
        * (
            model.Fw[ep, p]
            + sum(
                model.Fp[ep_, p_, ep, p]
                for ep_, p_ in model.EP_P
                if (ep, p) != (ep_, p_)
            )
        )
    )


def lower_level_constraint_3_rule(model, ep, p):
    '''
    Regla para añadir la tercera restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de igualdad.

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: restricción
    '''

    return lower_level_constraint_3(model, ep, p) == 0


def lower_level_constraint_4(model, ep, p):
    '''
    Expresión de la cuarta restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: expresión de la restricción
    '''

    return (
        -model.Fw[ep, p]
        - sum(
            model.Fp[ep_, p_, ep, p]
            for ep_, p_ in model.EP_P
            if (ep, p) != (ep_, p_)
        )
        + sum(
            model.Fp[ep, p, ep_, p_]
            for ep_, p_ in model.EP_P
            if (ep, p) != (ep_, p_)
        )
    )


def lower_level_constraint_4_rule(model, ep, p):
    '''
    Regla para añadir la cuarta restricción del problema de una empresa con respecto a uno de sus procesos.
    Restricción de desigualdad

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :return: restricción
    '''

    return lower_level_constraint_4(model, ep, p) <= 0


def mu_constraint_rule(model, ep, p, c):
    '''
    Regla para añadir la restricción de no negatividad del multiplicador (mu)
    asociado a la restricción c de un proceso de una empresa

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :param c: identiicador de la restricción
    :return: restricción
    '''

    return model.mu[ep, p, c] >= 0


def mu_2_constraint_rule(model, ep, p, ep_, p_):
    '''
    Regla para añadir la restricción de no negatividad del multiplicador (mu)
    asociado a la segunda restricción de un proceso de una empresa

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: restricción
    '''

    return model.mu_2[ep, p, ep_, p_] >= 0


def select_constraint_rule(model, ep, p, c):
    '''
    Selecciona una restricción asociada al problema de la empresa ep con su proceso p

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :param c: identificador de la restricción
    :return: restricción
    '''

    if c == 1:
        return lower_level_constraint_1_rule(model, ep, p)
    
    else:  # c == 4
        return lower_level_constraint_4_rule(model, ep, p)


def select_constraint(model, ep, p, c):
    '''
    Seleccionar la expresión de una restricción asociada al problema de la empresa ep con su proceso p

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :param c: identificador de la restricción
    :return: restricción
    '''

    if c == 1:
        return lower_level_constraint_1(model, ep, p)
    
    else:  # c == 4
        return lower_level_constraint_4(model, ep, p)


def complementarity_rule(model, ep, p, c):
    '''
    Regla para añadir la restricción de complementariedad asociada a una restricción del problema de una empresa para uno de sus procesos

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa
    :param p: identificador del proceso
    :param c: identificador de la restricción
    :return: restricción de complementariedad
    '''

    expr_const = select_constraint_rule(model, ep, p, c)

    return complements(mu_constraint_rule(model, ep, p, c), expr_const)


def complementarity_2_rule(model, ep, p, ep_, p_):
    '''
    Regla para añadir la restricción de complementariedad asociada a la segunda restricción del problema de una empresa para uno de sus procesos

    :param model: instancia de un modelo abstracto
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: restricción de complementariedad
    '''
    
    return complements(mu_2_constraint_rule(model, ep, p, ep_, p_), lower_level_constraint_2_rule(model, ep, p, ep_, p_))


def lagrangian_expr(model, ep, p, ep_, p_):
    '''
    Solo toma los gradientes con respecto a los Fp del problema de la empresa ep 
    Expresión de lagrangiana del problema de una empresa con respecto a una de las variables (Fp[ep, p, ep_, p_])

    :param model: instancia de un modelo abstracto
    :param ep_prob: identificador del problema de una empresa (es el identificador de una empresa)
    :param ep: identificador de la empresa que envía
    :param p: identificador del proceso que envía
    :param ep_: identificador de la empresa que recibe
    :param p_: identificador del proceso que recibe
    :return: restricción
    '''
    
    if (ep, p, ep_, p_) not in model.EP_P_EP_P:
        return Constraint.Skip

    objective_gradient = differentiate(
        lower_level_objective_rule(model, ep),
        wrt=model.Fp[ep, p, ep_, p_],
        mode='sympy',
    )

    expr = objective_gradient

    constraint_2_gradient = - model.mu_2[ep, p, ep_, p_] * differentiate(
        lower_level_constraint_2(model, ep, p, ep_, p_),
        wrt=model.Fp[ep, p, ep_, p_],
        mode='sympy',
    )
    
    expr += constraint_2_gradient 

    # siempre se halla el diferencial con respecto a la misma variable 
    for ep_1, p_1 in model.EP_P: # analizar todas las restricciones de la 
                                 # empresa ep (de cada tipo de restricción hay tantas como procesos tiene la empresa)
        if ep == ep_1: # comprobar si p_1 es proceso de la empresa actual
            
            # calcular el gradiente de la restricción 1 del proceso p_1 con respecto a Fp[e, p, ep_, p_]
            # model.mu[ep, p_1, 1] multiplicador de la restriccion 1 del proceso p_1 de la empresa ep
            constraint_1_gradient = model.mu[ep, p_1, 1] * differentiate(
                lower_level_constraint_1(model, ep, p_1),
                wrt=model.Fp[ep, p, ep_, p_],
                mode='sympy',
            )

            constraint_3_gradient = model.lmbd[ep, p_1] * differentiate(
                lower_level_constraint_3(model, ep, p_1),
                wrt=model.Fp[ep, p, ep_, p_],
                mode='sympy',
            )

            constraint_4_gradient = model.mu[ep, p_1, 4] * differentiate(
                lower_level_constraint_4(model, ep, p_1),
                wrt=model.Fp[ep, p, ep_, p_],
                mode='sympy',
            )

            expr += (
                constraint_1_gradient
                + constraint_3_gradient
                + constraint_4_gradient
            )

    return expr == 0
