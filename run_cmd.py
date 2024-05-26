import subprocess

methods = ['method1', 'method2', 'method3']  # Replace with your actual methods
scenes = ['scene1', 'scene2', 'scene3']  # Replace with your actual scenes

for m in methods:
    for s in scenes:
        command = f'python graphics/metrics.py --name {s} --method {m}'
        print(f'Running command: {command}')
        subprocess.run(command, shell=True, check=True)

        