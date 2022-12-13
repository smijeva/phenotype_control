import functools
import unittest
import biodivine_aeon as ba
from pathlib import Path

from perturbed_graph import PerturbedGraph


class TestControllableBooleanNetwork(unittest.TestCase):
    def setUp(self) -> None:
        model_string = Path('toy.aeon').read_text()
        self.bn = ba.BooleanNetwork.from_aeon(model_string)

    def test_permanent(self):
        pg = PerturbedGraph(self.bn)
        stg = ba.SymbolicAsyncGraph(pg.perturbed_bn)
        att = ba.find_attractors(stg)

        var_id = pg.perturbed_bn.find_variable("A")
        phenotype_non_compliant_space = stg.fix_variable(var_id, False)

        folded_att = functools.reduce(ba.ColoredVertexSet.union, att, stg.empty_colored_vertices())
        bad_colors = folded_att.intersect(phenotype_non_compliant_space).colors()


        ok_colors = stg.unit_colors().minus(bad_colors)

        assert len(att) > 0
