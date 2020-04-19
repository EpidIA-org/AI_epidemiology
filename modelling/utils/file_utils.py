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
                         start_day, end_day,
                         output_filename):
    columns = ["jour"] + values_names
    sampled_pts_nb = len(times)
    final_res = pd.DataFrame(
        np.zeros((sampled_pts_nb,
                  len(columns))),
        columns=columns)

    final_res["jour"] = times
    final_res[values_names] = predictions

    step = int(sampled_pts_nb / (end_day - start_day))
    indices = list(range(0,
                         sampled_pts_nb,
                         step))
    final_res = final_res.iloc[indices, :]
    final_res.jour = final_res.jour.astype(np.int)

    final_res.to_csv(output_filename, index=False)
