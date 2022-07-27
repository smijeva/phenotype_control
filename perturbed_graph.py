import biodivine_aeon as ba
import parameter_names_generator as ppg

from typing import List, Dict


class PerturbedGraph:
    def __init__(self,
                 original_bn: ba.BooleanNetwork,
                 can_over_express: List[ba.VariableId] = None,
                 can_knockout: List[ba.VariableId] = None):
        if can_over_express is None:
            can_over_express = original_bn.variables()
        if can_knockout is None:
            can_knockout = original_bn.variables()

        normalized_bn = self._normalize_bn(original_bn)

        self._make_perturbed_and_original_bns(normalized_bn,
                                              can_over_express=can_over_express,
                                              can_knockout=can_knockout)

    """
    Create a copy of the given `model`, but make every regulation non-observable, and add an
    unspecified auto-regulation to each variable (that does not have an autoregulation already).
    Additionally, convert every implicit update function to and explicit parameter.
    """

    @staticmethod
    def _normalize_bn(original_bn: ba.BooleanNetwork) -> ba.BooleanNetwork:
        # Copy graph, but with non-observable regulations.
        variable_names = [original_bn.get_variable_name(v) for v in original_bn.variables()]
        normalized_rg = ba.RegulatoryGraph(variable_names)
        for r in original_bn.graph().regulations():
            r['observable'] = False
            normalized_rg.add_regulation(r)

        normalized_bn = ba.BooleanNetwork(normalized_rg)

        # Copy parameters
        for p in original_bn.parameters():
            normalized_bn.add_parameter({"name": original_bn.get_parameter_name(p),
                                         "arity": original_bn.get_parameter_arity(p)})

        # Copy update functions
        for v in original_bn.variables():
            orig_function = original_bn.get_update_function(v)
            if orig_function is not None:
                normalized_bn.set_update_function(v, orig_function)
            else:
                par_regulators = [normalized_bn.get_variable_name(r) for r in normalized_rg.regulators(v)]
                par_name = ppg.get_explicit_update_function_parameter_from_var(original_bn, v)
                normalized_bn.add_parameter({"name": par_name,
                                             "arity": len(par_regulators)})
                normalized_bn.set_update_function(v, f"{par_name}({','.join(par_regulators)})")

        return normalized_bn

    def _make_perturbed_and_original_bns(self,
                                         normalized_bn: ba.BooleanNetwork,
                                         can_over_express: List[ba.VariableId] = None,
                                         can_knockout: List[ba.VariableId] = None):
        self.perturbed_bn = ba.BooleanNetwork(normalized_bn.graph())
        self.unperturbed_bn = ba.BooleanNetwork(normalized_bn.graph())

        # Copy existing parameters from the original network
        for par in normalized_bn.parameters():
            self.perturbed_bn.add_parameter({"name": normalized_bn.get_parameter_name(par),
                                             "arity": normalized_bn.get_parameter_arity(par)})
            self.unperturbed_bn.add_parameter({"name": normalized_bn.get_parameter_name(par),
                                               "arity": normalized_bn.get_parameter_arity(par)})

        # Add perturbation parameters
        self.perturbation_params = {}
        for var in reversed(normalized_bn.variables()):
            # Function exists thanks to the normalization in the previous step
            original_function = normalized_bn.get_update_function(var)
            assert original_function is not None

            ko_par_name = ppg.get_knockout_from_var(normalized_bn, var)
            oe_par_name = ppg.get_over_expression_from_var(normalized_bn, var)
            if var in can_knockout and var in can_over_express:
                ko_par = self.perturbed_bn.add_parameter({"name": ko_par_name, "arity": 0})
                ko_par2 = self.unperturbed_bn.add_parameter({"name": ko_par_name, "arity": 0})
                assert (ko_par == ko_par2)
                oe_par = self.perturbed_bn.add_parameter({"name": oe_par_name, "arity": 0})
                oe_par2 = self.unperturbed_bn.add_parameter({"name": oe_par_name, "arity": 0})
                assert (oe_par == oe_par2)
                self.perturbed_bn.set_update_function(var, f"!{ko_par_name} & ({oe_par_name} | ({original_function}))")
                self.unperturbed_bn.set_update_function(var, f"({ko_par_name} | !{ko_par_name}) "
                                                             f" & ({oe_par_name} | !{oe_par_name}) "
                                                             f" & ({original_function})")
                self.perturbation_params[var] = [ko_par, oe_par]
            elif var in can_knockout:
                ko_par = self.perturbed_bn.add_parameter({"name": ko_par_name, "arity": 0})
                ko_par2 = self.unperturbed_bn.add_parameter({"name": ko_par_name, "arity": 0})
                assert (ko_par == ko_par2)
                self.perturbed_bn.set_update_function(var, f"!{ko_par_name} & ({original_function})")
                self.unperturbed_bn.set_update_function(var, f"({ko_par_name} | !{ko_par_name}) "
                                                             f" & ({original_function})")
                self.perturbation_params[var] = [ko_par]
            elif var in can_over_express:
                oe_par = self.perturbed_bn.add_parameter({"name": oe_par_name, "arity": 0})
                oe_par2 = self.unperturbed_bn.add_parameter({"name": oe_par_name, "arity": 0})
                assert (oe_par == oe_par2)
                self.perturbed_bn.set_update_function(var, f"{oe_par_name} | ({original_function})")
                self.unperturbed_bn.set_update_function(var, f"({oe_par_name} | !{oe_par_name}) "
                                                             f" & ({original_function})")
                self.perturbation_params[var] = [oe_par]
            else:
                self.perturbed_bn.set_update_function(var, original_function)
                self.perturbation_params[var] = []

    def permanent_control(self, phenotype: Dict[str, bool]):
        stg = ba.SymbolicAsyncGraph(self.perturbed_bn)

        phenotype_compliant_space = stg.unit_colored_vertices()
        for var, val in phenotype.values():
            var_id = self.perturbed_bn.find_variable(var)
            fix = stg.fix_variable(var_id, val)
            phenotype_compliant_space = phenotype_compliant_space.intersect(fix)

        attractors = ba.find_attractors(stg)
