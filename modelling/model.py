"""
Model implementation
"""
import argparse
import datetime
import json
import os

import numpy as np
from scipy.integrate import odeint

from gradients_computations_funcs import gradients_computations_SIRDepModel
from utils.file_utils import save_predictions_csv, read_json_file
from utils.viz_utils import savefig


class Model(object):
    """
    Model class :
    - read parameters of model from config file
    - resolve ode
    - save figure and csv file of the solution

    model_config_json (str): filename of config file (json format)
    output_folder (str): path where to save fig and predictions
    gradients_computations_funct (funct) : function that computes
                                           gradient of ode
    """
    def __init__(self, model_config_json, output_folder,
                 gradients_computations_funct):

        self.config = read_json_file(model_config_json)
        self.output_folder = os.path.abspath(output_folder)
        os.makedirs(self.output_folder, exist_ok=True)

        if not self.check():
            print("keys are missing in %s" % model_config_json)

        self.init_model_parameters()

        self.gradients_computations_funct =  \
            gradients_computations_funct

    def read_config(self, filename):
        with open(filename) as json_data:
            config = json.load(json_data)
        return config

    def check(self):
        """check if all keys are in config file"""
        config_keys = ["name", "values_names",
                       "initial_values", "params", "start_day",
                       "end_day", "sampled_pts_nb"]
        if set(config_keys) - set(self.config.keys()):
            return False
        return True

    def init_model_parameters(self):
        """initialize all parameters of model"""
        # read model name
        self.model_name = self.config["name"]

        # read departements
        self.deps = self.config["params"]["deps"]
        self.nb_deps = len(self.config["params"]["deps"])

        # read variable names
        self.values_names = self.config["values_names"]

        # read initial values
        initial_values = \
            [self.config["initial_values"][name]
             for name in self.config["values_names"]]
        self.initial_values = [item
                               for sublist in initial_values
                               for item in sublist]

        assert(len(self.values_names) * self.nb_deps ==
               len(self.initial_values))

        # read ode parameters
        self.params = self.config["params"]

        self.start_day = datetime.datetime.strptime(
            self.config["start_day"], '%d-%m-%Y')
        self.end_day = datetime.datetime.strptime(
            self.config["end_day"], '%d-%m-%Y')
        self.nb_days = (self.end_day - self.start_day).days
        self.days = [self.start_day + datetime.timedelta(days=i)
                     for i in range(self.nb_days)]
        self.sampled_pts_nb = self.config["sampled_pts_nb"]

        self.times = np.linspace(
            0,
            self.nb_days,
            self.sampled_pts_nb)

    def resolution(self):
        """ode resolution"""
        self.predictions = np.array(odeint(self.gradients_computations_funct,
                                           self.initial_values,
                                           self.times,
                                           args=(self.params,)))

    def save_plot(self):
        """save figure of the solution"""
        filename = os.path.join(
            self.output_folder, "%s_model_fig.png" % self.model_name)
        savefig(filename, self.predictions,
                self.times, self.values_names,
                self.deps, self.model_name)

    def save_predictions(self):
        """save preditions"""
        filename = os.path.join(self.output_folder,
                                "%s_model_predictions.csv" % self.model_name)

        save_predictions_csv(self.predictions, self.values_names, self.times,
                             self.days, self.deps,
                             filename)

    def run(self):
        self.resolution()
        self.save_plot()
        self.save_predictions()


def arguments():
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument(
        'model_config_json', help='configuration of model')
    parser.add_argument(
        'output_folder', help='output folder')
    return parser.parse_args()


def main(args):
    model = Model(args.model_config_json,
                  args.output_folder,
                  gradients_computations_SIRDepModel)
    model.run()


if __name__ == "__main__":
    args = arguments()
    main(args)
