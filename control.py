import datetime
from typing import Dict
import biodivine_aeon as ba
import itertools as it

import parameter_names_generator
from perturbed_graph import PerturbedGraph
from functools import reduce


def powerset(lst):
    return reduce(lambda result, x: result + [subset + [x] for subset in result], lst, [[]])


def my_find_attractors(graph: ba.SymbolicAsyncGraph, space: ba.ColoredVertexSet):
    states = ba.transition_guided_reduction(
        graph,
        space,
    )
    return ba.xie_beerel_attractors(
        graph,
        states
    )


def permanent_control(pg: PerturbedGraph, phenotype: Dict[str, bool]):
    stg = pg.get_perturbed_stg()

    phenotype_compliant_space = stg.unit_colored_vertices()
    for var, val in phenotype.items():
        var_id = stg.network().find_variable(var)
        fix = stg.fix_variable(var_id, val)
        phenotype_compliant_space = phenotype_compliant_space.intersect(fix)

    print('Starting space restricting', str(datetime.datetime.now()))
    perturbations_violating_space = stg.unit_colored_vertices()

    for var_id in stg.network().variables():
        oe_par_name = parameter_names_generator.get_over_expression_from_var(stg.network(), var_id)
        ko_par_name = parameter_names_generator.get_knockout_from_var(stg.network(), var_id)

        # Both KO and OE cannot be true at the same time
        knockout_and_overexpression = (stg.unit_colored_vertices()
                                          .intersect_colors(stg.fix_parameter(oe_par_name, True))
                                          .intersect_colors(stg.fix_parameter(ko_par_name, True)))
        outside_overexpression = (stg.unit_colored_vertices()
                                     .intersect_colors(stg.fix_parameter(oe_par_name, True))
                                     .intersect(stg.fix_variable(var_id, False)))
        outside_knockout = (stg.unit_colored_vertices()
                               .intersect_colors(stg.fix_parameter(ko_par_name, True))
                               .intersect(stg.fix_variable(var_id, True)))

        perturbations_violating_space = (perturbations_violating_space.minus(knockout_and_overexpression)
                                                                      .minus(outside_overexpression)
                                                                      .minus(outside_knockout))

    print('Ending space restricting', str(datetime.datetime.now()))

    # Find attractors outside the phenotype (spurious attractors)
    phenotype_violating_space = (stg.unit_colored_vertices()
                                    .minus(phenotype_compliant_space)
                                    .minus(perturbations_violating_space))
    attractors = my_find_attractors(stg, phenotype_violating_space)
    all_attractors = stg.empty_colored_vertices()
    for a in attractors:
        spurious_attractors = all_attractors.union(a)

    # The params (colours x perturbations) which do not violate the phenotype are OK
    return stg.unit_colors().minus(spurious_attractors.colors())
