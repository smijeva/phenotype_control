import biodivine_aeon as ba
from perturbed_graph import PerturbedGraph


class ControlMap:
    def __init__(self,
                 context: PerturbedGraph,
                 perturbation_set: ba.ColorSet):
        self.context = context
        self.perturbation_set = perturbation_set

