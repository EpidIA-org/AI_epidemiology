from azureml.core import Experiment, Workspace, Run
import azureml.core
import numpy as np
import random, os
from tqdm import tqdm

ws = Workspace.from_config()
print(f"[INFO] Connected to workspace {ws.name}")

experiment = Experiment(workspace=ws, name='logging-api-test')
print(f"[INFO] Connected to experiment {experiment.name}")

def doRun(scale_factor, category):
    # start logging for the run
    run = experiment.start_logging()

    # log a string metric
    run.log(name='Category', value=category)

    # log numerical values
    run.log(name="scale factor", value = scale_factor)
    run.log(name='Magic Number', value=42 * scale_factor)

    # logging vectors
    fibonacci_values = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    scaled_values = (i * scale_factor for i in fibonacci_values)

    # Log a list of values. Note this will generate a single-variable line chart.
    run.log_list(name='Fibonacci', value=scaled_values)

    for i in tqdm(range(-10, 10)):
        # log a metric value repeatedly, this will generate a single-variable line chart.
        run.log(name='Sigmoid', value=1 / (1 + np.exp(-i)))

    # logging tables
    
    # create a dictionary to hold a table of values
    sines = {}
    sines['angle'] = []
    sines['sine'] = []

    for i in tqdm(range(-10, 10)):
        angle = i / 2.0 * scale_factor
        
        # log a 2 (or more) values as a metric repeatedly. This will generate a 2-variable line chart if you have 2 numerical columns.
        run.log_row(name='Cosine Wave', angle=angle, cos=np.cos(angle))
            
        sines['angle'].append(angle)
        sines['sine'].append(np.sin(angle))

    # log a dictionary as a table, this will generate a 2-variable chart if you have 2 numerical columns
    run.log_table(name='Sine Wave', value=sines)

    # logging images

    # Create a plot
    import matplotlib.pyplot as plt
    angle = np.linspace(-3, 3, 50) * scale_factor
    plt.plot(angle,np.tanh(angle), label='tanh')
    plt.legend(fontsize=12)
    plt.title('Hyperbolic Tangent', fontsize=16)
    plt.grid(True)

    # Log the plot to the run.  To log an arbitrary image, use the form run.log_image(name, path='./image_path.png')
    run.log_image(name='Hyperbolic Tangent', plot=plt)

    os.makedirs('outputs', exist_ok=True)
    output_file = os.path.join('outputs','myfile.txt')
    with open(output_file, "w") as f:
        f.write("This is an output file that will be automatically uploaded.")

    run.upload_file(name=output_file, path_or_stream=output_file)
    run.complete()

    return run.id

categories = ['Red', 'Green', 'Yellow']

for i in range(5):
    cat = categories[random.randint(0,2)]
    scale_factor = random.uniform(0.8, 2.5)
    run_id = doRun(scale_factor, cat);
    print(f"Finished run with id {run_id}")


print("\nAll Done!!!")

