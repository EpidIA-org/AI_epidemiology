##model

in order the to run a simulation for a new model, you need to :

1- write a config file that contains the parameters of the model according to this format

```json
{
	"name" : "SIR",
	"values_nb" : 3,
	"values_names" : ["S", "I", "R"],
	"initial_values" : {"S" : 0.9,
						"I" : 0.1,
					    "R" : 0.0},
	"params" : {"beta" : 19,
				"gamma" : 0.9},
	"start_day" : 0,
	"end_day" : 100,
	"sampled_pts_nb" : 10000
}
```

2- implement the gradients computations function of model in gradients_computation_funcs.py according to this format :

```python
def gradients_computations_SIRModel(data, t, params):
    print(data)
    S, I, R = data
    dS_dt = -params["beta"] * S * I
    dI_dt = params["beta"] * S * I - params["gamma"] * I
    dR_dt = params["gamma"] * I
    return([dS_dt, dI_dt, dR_dt])
```

3 - run in terminal :

```bash 
python model.py config/sir_modelling.json outputs/
```

you will find a figure and csv file of predictions of the model