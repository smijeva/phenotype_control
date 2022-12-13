# import unittest
# import biodivine_aeon as ba
# from pathlib import Path
#
# from perturbed_graph import PerturbedGraph
# import parameter_names_generator as ppg
#
#
# class TestControllableBooleanNetwork(unittest.TestCase):
#     def setUp(self) -> None:
#         model_string = Path('toy.aeon').read_text()
#         self.bn = ba.BooleanNetwork.from_aeon(model_string)
#         self.knck_a = ppg.get_knockout_from_name("A")
#         self.knck_b = ppg.get_knockout_from_name("B")
#         self.knck_c = ppg.get_knockout_from_name("C")
#         self.ovrex_a = ppg.get_over_expression_from_name("A")
#         self.ovrex_b = ppg.get_over_expression_from_name("B")
#         self.ovrex_c = ppg.get_over_expression_from_name("C")
#
#     def test_default(self):
#         cbn = PerturbedGraph(self.bn).cbn
#
#         self.assertEquals(f"(!{self.knck_a} & ({self.ovrex_a} | (A | B)))", cbn.get_update_function("A"))
#         self.assertEquals(f"(!{self.knck_b} & ({self.ovrex_b} | (A & C)))", cbn.get_update_function("B"))
#         self.assertEquals(f"(!{self.knck_c} & ({self.ovrex_c} | (A | !C)))", cbn.get_update_function("C"))
#
#     def test_can_over_express_b(self):
#         cbn = PerturbedGraph(self.bn, can_over_express=[self.bn.find_variable("B")], can_knockout=[]).cbn
#
#         self.assertEquals(f"(A | B)", cbn.get_update_function("A"))
#         self.assertEquals(f"({self.ovrex_b} | (A & C))", cbn.get_update_function("B"))
#         self.assertEquals(f"(A | !C)", cbn.get_update_function("C"))
#
#     def test_can_knockout_b(self):
#         cbn = PerturbedGraph(self.bn, can_over_express=[], can_knockout=[self.bn.find_variable("B")]).cbn
#
#         self.assertEquals(f"(A | B)", cbn.get_update_function("A"))
#         self.assertEquals(f"(!{self.knck_b} & (A & C))", cbn.get_update_function("B"))
#         self.assertEquals(f"(A | !C)", cbn.get_update_function("C"))
#
#
