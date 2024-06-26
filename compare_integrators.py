from metrics import read_png, calculate_mse
import itertools
import json
import matplotlib.pyplot as plt
import numpy as np

scenes = ['ball', 'cbox', 'torus', 'veach_bidir', 'veach_mi', 'medium', 'glass', 'bathroom']
integrators = ['path', 'volpath', 'bdpt', 'pssmlt', 'mlt', 'erpt', 'sppm']

duration = dict()
with open('./log-server/db.json', 'r') as file:
    # Parse the JSON data into a Python dictionary
    for entry in json.load(file)["log"]:
        duration[(entry["scene"], entry["integrator"], entry["n_steps"])] = entry["duration_seconds"]

def read_images_and_duration(scene, integrator):
    indicies = [2 ** i for i in range(0, 10)]
    return [(read_png(f'./exr/{scene}_{integrator}.{index}.png'), duration[(scene, integrator, index)]) for index in indicies]


color_map = plt.get_cmap('tab10', len(integrators))
for scene in scenes:
    All_X = list()
    All_Y = list()
    # G = list()
    standard_image = read_png(f'./exr/{scene}.standard.png')
    plt.figure(figsize=(8, 16))
    plt.title(f'Scene = {scene}')
    for group_idx, integrator in enumerate(integrators):
        current_images_and_duration = read_images_and_duration(scene, integrator)
        duration_and_mse = [(p[1], calculate_mse(p[0], standard_image)) for p in current_images_and_duration]
        duration_and_mse = [p for p in duration_and_mse if not np.isnan(p[1])]
        X = [p[0] for p in duration_and_mse]
        Y = [p[1] for p in duration_and_mse]
        G = [group_idx for p in duration_and_mse]
        plt.plot(X, Y, marker='o', label=integrator)
        All_X += X
        All_Y += Y
    # plt.colorbar(label="Integrators")
    All_X = np.array(All_X)
    All_Y = np.array(All_Y)
    plt.legend(title='Integrators', loc='lower right')
    plt.xlabel('Duration (seconds)')
    plt.ylabel('MSE')
    # plt.xlim(0, np.median(All_X))
    plt.ylim(0, np.median(All_Y))
    plt.xlim(0, np.max(All_X[All_Y <= np.median(All_Y)]))
    plt.savefig(f'./saved_pics/{scene}.png')
    plt.close()

