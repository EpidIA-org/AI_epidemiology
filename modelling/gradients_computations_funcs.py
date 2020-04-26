"""
gradients computations functions for different models
"""

import numpy as np


def gradients_computations_SIRDepModel(data, t, params):
    nb_deps = len(params["deps"])
    nb_vars = params["nb_variables"]

    assert(len(data) == nb_vars * nb_deps)

    S = np.array([data[i] for i in range(0 * nb_deps, 1 * nb_deps)])
    I = np.array([data[i] for i in range(1 * nb_deps, 2 * nb_deps)])
    R = np.array([data[i] for i in range(2 * nb_deps, 3 * nb_deps)])

    beta = np.array(params["beta"])
    gamma = np.array(params["gamma"])
    M_di_dj = np.array(params["M_di_dj"]).reshape((nb_deps, nb_deps))

    dS_dt = np.zeros(S.shape)
    for i in range(nb_deps):
        val = -beta[i] * S[i] * I[i]
        for j in range(nb_deps):
            val += -beta[j] * S[i] * M_di_dj[i, j] * I[j] + \
                -beta[i] * S[i] * M_di_dj[i, j] * I[j]
        dS_dt[i] = float(val) / nb_deps
    dI_dt = - dS_dt - np.multiply(gamma, I)
    dR_dt = np.multiply(gamma, I)

    dydt = []
    dydt.extend(list(dS_dt))
    dydt.extend(list(dI_dt))
    dydt.extend(list(dR_dt))

    return(dydt)
