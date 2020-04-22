"""
Model implementation
"""
import argparse
import json
import os

import numpy as np
from scipy.integrate import odeint

from gradients_computations_funcs import gradients_computations_SIRModel
from utils.file_utils import save_predictions_csv, read_json_file
from utils.viz_utils import savefig


class Model(object):
    """
    Moodel object 
    read parameters of model from config file
    resolve ode
    save figure and csv file of the solution
    """

    def __init__(self, model_config_json, output_folder,
                 gradient_computations_funct):

        self.config = read_json_file(model_config_json)
        self.output_folder = os.path.abspath(output_folder)
        os.makedirs(self.output_folder, exist_ok=True)

        if not self.check():
            print("keys are missing in %s" % model_config_json)

        self.init_model_parameters()

        self.gradients_computations_funct =  \
            gradients_computations_SIRModel

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
        self.model_name = self.config["name"]
        self.values_names = self.config["values_names"]
        self.initial_values = \
            [self.config["initial_values"][name]
             for name in self.config["values_names"]]
        assert(len(self.values_names) == len(self.initial_values))

        self.params = self.config["params"]
        self.start_day = self.config["start_day"]
        self.end_day = self.config["end_day"]
        self.sampled_pts_nb = self.config["sampled_pts_nb"]

        self.times = np.linspace(
            self.start_day,
            self.end_day,
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
                self.model_name)

    def save_predictions(self):
        """save preditions"""
        filename = os.path.join(self.output_folder,
                                "%s_model_predictions.csv" % self.model_name)

        save_predictions_csv(self.predictions, self.values_names, self.times,
                             self.start_day, self.end_day,
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
                  gradients_computations_SIRModel)
    model.run()


if __name__ == "__main__":
    args = arguments()
    main(args)
