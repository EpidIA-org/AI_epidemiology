"""
gradients computations functions for different model
"""

import numpy as np

def gradients_computations_SIRDepModel(data, t, params):
    nb_dep = params["nb_dep"]

    assert(len(data) == 3 * nb_dep)

    S = np.array([data[i] for i in range(0 * nb_dep, 1 * nb_dep)])
    I = np.array([data[i] for i in range(1 * nb_dep, 2 * nb_dep)])
    R = np.array([data[i] for i in range(2 * nb_dep, 3 * nb_dep)])

    beta = np.array(params["beta"])
    gamma = np.array(params["gamma"])

    M_di_dj = np.array(params["M_di_dj"]).reshape((nb_dep, nb_dep))

    dS_dt = np.zeros(S.shape)
    for i in range(nb_dep):
        val = -beta[i] * S[i] * I[i]
        for j in range(nb_dep):
            val += -beta[j] * S[i] * M_di_dj[i,j] * I[j] + \
                -beta[i] * S[i] * M_di_dj[i,j] * I[j]
        dS_dt[i] = float(val) / nb_dep

    dI_dt = - dS_dt - np.multiply(gamma,I)


    dR_dt = np.multiply(gamma,I)

    dydt = []

    dydt.extend(list(dS_dt))
    dydt.extend(list(dI_dt))
    dydt.extend(list(dR_dt))

    return(dydt)
