"""
Desc
"""
import json

import numpy as np
import pandas as pd


def read_json_file(filename):
    with open(filename) as json_data:
        config = json.load(json_data)
    return config


def save_predictions_csv(predictions, values_names, times,
                         days, deps,
                         output_filename):
    """
    save outputs as a csv file
    with the following columns :
    [date, dep, var1, var2, ...]

    predictions (array): predictions of model
    values_names (list): variables names
    times (array): time series of resolution
    days (list): list of days
    deps (list): list of departement
    output_filename (str): path where to save csv
    """
    values_deps = ["%s_%s" % (val, dep)
                   for val in values_names for dep in deps]
    columns = ["date"] + values_deps
    sampled_pts_nb = len(times)
    nb_days = len(days)
    step = int(sampled_pts_nb / (nb_days - 1))
    indices = list(range(0,
                         sampled_pts_nb,
                         step))

    assert(len(indices) == nb_days)

    df_res = pd.DataFrame(
        np.zeros((sampled_pts_nb,
                  len(columns))),
        columns=columns)
    df_res[values_deps] = predictions
    df_res = df_res.iloc[indices, :]
    df_res["date"] = days

    columns = ["date"] + ["dep"] + values_names
    df_final_res = pd.DataFrame()
    for dep in deps:
        df = pd.DataFrame(
            np.zeros((nb_days,
                      len(columns))),
            columns=columns)
        df["dep"] = dep
        df["date"] = days
        values = ["%s_%s" % (name, dep) for name in values_names]
        df[values_names] = df_res[values].values
        df_final_res = df_final_res.append(df)

    df_final_res.to_csv(output_filename, index=False)
