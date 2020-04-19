"""
Desc
"""
import matplotlib.pyplot as plt


def savefig(filename, predictions,
              times, values_names,
              model_name):
    plt.figure(figsize=[6, 4])
    for i, name in enumerate(values_names):
        plt.plot(times,
                 predictions[:, i],
                 label="%s(t)" % name)
    plt.grid()
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Proportions")
    plt.title("%s model" % model_name)

    plt.savefig(filename)
