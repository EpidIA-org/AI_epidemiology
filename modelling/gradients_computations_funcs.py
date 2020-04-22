"""
gradients computations functions for different model
"""

def gradients_computations_SIRModel(data, t, params):
    S, I, R = data
    dS_dt = -params["beta"] * S * I
    dI_dt = params["beta"] * S * I - params["gamma"] * I
    dR_dt = params["gamma"] * I
    return([dS_dt, dI_dt, dR_dt])


def gradients_computations_V1Model(data, t, params):
    S_d1, S_d2, E_d1, E_d2, I_d1, I_d2, A_d1, A_d2, \
        H_d1, H_d2, ICU_d1, ICU_d2, \
        R_d1, R_d2, D_d1, D_d2 = data

    beta_d1 = params["beta_d1"]
    beta_d2 = params["beta_d2"]
    M_d1_d2 = params["M_d1_d2"]
    M_d2_d1 = params["M_d1_d2"]

    TE = params["TE"]
    TI = params["TI"]
    TH = params["TH"]
    TA = params["TA"]
    TICU = params["TICU"]

    rho_d1 = params["rho_d1"]
    lambda_d1 = params["lambda_d1"]
    gamma_d1 = params["gamma_d1"]

    rho_d2 = params["rho_d2"]
    lambda_d2 = params["lambda_d2"]
    gamma_d2 = params["gamma_d2"]

    dS_d1_dt = -beta_d1 * S_d1 * (I_d1 + A_d1) + \
        -beta_d2 * S_d1 * M_d1_d2 * (I_d2 + A_d2) + \
        -beta_d1 * S_d1 * M_d1_d2 * (I_d2 + A_d2)

    dS_d2_dt = -beta_d2 * S_d2 * (I_d2 + A_d2) + \
        -beta_d1 * S_d2 * M_d1_d2 * (I_d1 + A_d1) + \
        -beta_d2 * S_d2 * M_d2_d1 * (I_d1 + A_d1)

    dE_d1_dt = dS_d1_dt - dS_d1_dt(t - TE)
    dE_d2_dt = dS_d2_dt - dS_d2_dt(t - TE)

    dI_d1_dt = dE_d1_dt - dE_d1_dt(t - TI)
    dI_d2_dt = dE_d2_dt - dE_d2_dt(t - TI)

    dH_d1_dt = rho_d1 * (dI_d1_dt - dI_d1_dt(t - TH))
    dH_d2_dt = rho_d2 * (dI_d2_dt - dI_d2_dt(t - TH))

    dICU_d1_dt = lambda_d1 * (dI_d1_dt - dI_d1_dt(t - TICU))
    dICU_d2_dt = lambda_d2 * (dI_d2_dt - dI_d2_dt(t - TICU))

    dA_d1_dt = (1 - lambda_d1 - rho_d1) * (dI_d1_dt - dI_d1_dt(t - TA))
    dA_d2_dt = (1 - lambda_d2 - rho_d2) * (dI_d2_dt - dI_d2_dt(t - TA))

    dD_d1_dt = gamma_d1 * dH_d1_dt(t - TH) + gamma_d1 * dICU_d1_dt(t - TICU)
    dD_d2_dt = gamma_d2 * dH_d2_dt(t - TH) + gamma_d2 * dICU_d2_dt(t - TICU)

    dR_d1_dt = 0
    dR_d2_dt = 0

    return([dS_d1_dt, dS_d2_dt, dE_d1_dt, dE_d2_dt,
            dI_d1_dt, dI_d2_dt, dA_d1_dt, dA_d2_dt,
            dH_d1_dt, dH_d2_dt, dICU_d1_dt, dICU_d2_dt,
            dR_d1_dt, dR_d2_dt, dD_d1_dt, dD_d2_dt])
