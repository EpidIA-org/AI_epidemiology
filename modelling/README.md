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
	"params" : {
				"nb_variables" : 3,
				"deps" : [90, 91],
				"beta" : [19,11],
				"gamma" : [0.9,0.9],
				"M_di_dj" : [0.0, 1, 0.00, 0.01]},
	"start_day" : "01-01-2020",
	"end_day" : "15-02-2020",
	"sampled_pts_nb" : 10000
}
```

2- implement the gradients computations function of the model in gradients_computation_funcs.py according to this format :

```python
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

    return([list(dS_dt), list(dI_dt), list(dR_dt)])
```

3 - run in terminal :

```bash 
python model.py config/sir_modelling.json outputs/
```

you will find a figure and csv file of predictions in `outputs/` file 