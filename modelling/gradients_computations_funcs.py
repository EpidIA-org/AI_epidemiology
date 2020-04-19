"""
Desc
"""



def gradients_computations_SIRModel(data, times, params):
    S, I, R = data
    dS_dt = -params["beta"] * S * I
    dI_dt = params["beta"] * S * I - params["gamma"] * I
    dR_dt = params["gamma"] * I
    return([dS_dt, dI_dt, dR_dt])