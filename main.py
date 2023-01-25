# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import sys
from pathlib import Path
import time
import biodivine_aeon as ba


# Press the green button in the gutter to run the script.
from control import permanent_control
from perturbed_graph import PerturbedGraph

if __name__ == '__main__':
    print('start!')
    model_name = sys.argv[1]
    phenotype_name = sys.argv[2]
    print(model_name)
    print(phenotype_name)

    with open("phentoype_benchmark/benchmark.json") as handle:
        config = json.load(handle)

    model = config[model_name]['file']
    phenotype = config[model_name]['targets'][phenotype_name]

    bn = ba.BooleanNetwork.from_aeon(Path(f'./phentoype_benchmark/{model}').read_text())
    vars = bn.variables()
    rg = bn.graph()
    pg = PerturbedGraph(bn)

    start = time.time()
    permanent_control(pg, phenotype)
    end = time.time()
    print(f'permanent control {model_name}: {end - start}')



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
