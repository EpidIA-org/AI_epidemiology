"""
Desc
"""
import matplotlib.pyplot as plt


def savefig(filename, predictions,
            times, values_names, deps,
            model_name):
  plt.figure(figsize=[6, 4])
  values_deps = ["%s_%s" % (val, dep)
                 for val in values_names for dep in deps]
  for i, name in enumerate(values_deps):
    plt.plot(times,
             predictions[:, i],
             label="%s(t)" % name)
  plt.grid()
  plt.legend()
  plt.xlabel("Time")
  plt.ylabel("Proportions")
  plt.title("%s model" % model_name)

  plt.savefig(filename)
