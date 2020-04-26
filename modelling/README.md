# model

in order the to run a simulation for a new model, you need to :

1- write a config file that contains the parameters of the model according to this format

```json
{
	"name" : "SIR_n_dep",
	"values_names" : ["S", "I", "R"],
	"initial_values" : {"S" : [0.9,0.9],
						"I" : [0.1,0.1],
					    "R" : [0.0, 0.0]},
	"params" : {"nb_dep" : 2,
				"nb_variables" : 3,
				"beta" : [19,11],
				"gamma" : [0.9,0.9],
				"M_di_dj" : [0.0, 1, 0.00, 0.01]},
	"start_day" : 0,
	"end_day" : 20,
	"sampled_pts_nb" : 10000
}
```

2- implement the gradients computations function of the model in gradients_computation_funcs.py according to this format :

```python
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
```

3 - run in terminal :

```bash 
python model.py config/sir_modelling.json outputs/
```

you will find a figure and csv file of predictions in `outputs/` file 