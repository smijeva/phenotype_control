import datetime
import biodivine_aeon as ba
import parameter_names_generator
from perturbed_graph import PerturbedGraph
from typing import Dict
import itertools as it


# def my_find_attractors(graph: ba.SymbolicAsyncGraph, space: ba.ColoredVertexSet):
#     # Find all single-state attractors (in all space) -> easy
#     print(f"{datetime.datetime.now()} starting computing attractors...")
#     attractors_space = ba.FixedPoints.symbolic(graph, graph.unit_colored_vertices())
#
#     # Find relevant space to find complex attractors -> other attractors unreachable + relevant space
#     print(f"{datetime.datetime.now()} Fixed points computed, searching unexplored space (bwd)...")
#     bwd_reach_fixed_points = ba.reach_bwd(graph, attractors_space)
#     unexplored_space = space.minus(bwd_reach_fixed_points)
#
#     # Print stats
#     print(f"all {graph.unit_colored_vertices().cardinality()}")
#     print(f"explored {bwd_reach_fixed_points.cardinality()}")
#     print(f"unexplored {unexplored_space.cardinality()}")
#
#     # Search complex attractors in relevant space
#     print(f"{datetime.datetime.now()} Found unexpolored space, doing reduction...")
#     states = ba.transition_guided_reduction(
#         graph,
#         unexplored_space
#     )
#
#     print(f"{datetime.datetime.now()} Starting Xie Beerel...")
#     complex_attractors = ba.xie_beerel_attractors(
#         graph,
#         states
#     )
#
#     # Derive relevant spurious colours - all attractor colours sets in spurious space
#     print(f"{datetime.datetime.now()} Attractors found.")
#     for ca in complex_attractors:
#         attractors_space = attractors_space.union(ca)
#
#     return attractors_space.intersect(space)


def my_find_attractors(graph: ba.SymbolicAsyncGraph, space: ba.ColoredVertexSet):
    states = ba.transition_guided_reduction(
            graph,
            space
    )

    print(f"{datetime.datetime.now()} Starting Xie Beerel...")
    complex_attractors = ba.xie_beerel_attractors(
        graph,
        states
    )

    print(f"{datetime.datetime.now()} Attractors found.")

    attractors_space = graph.empty_colored_vertices()
    for ca in complex_attractors:
        attractors_space = attractors_space.union(ca)
    return attractors_space



def permanent_control(pg: PerturbedGraph, phenotype: Dict[str, bool], control_max_size=3):
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
        # When overexpression holds, the variable cannot gain False value
        outside_overexpression = (stg.unit_colored_vertices()
                                     .intersect_colors(stg.fix_parameter(oe_par_name, True))
                                     .intersect(stg.fix_variable(var_id, False)))
        # When knockout holds, the variable cannot gain True value
        outside_knockout = (stg.unit_colored_vertices()
                               .intersect_colors(stg.fix_parameter(ko_par_name, True))
                               .intersect(stg.fix_variable(var_id, True)))

        perturbations_violating_space = (perturbations_violating_space.minus(knockout_and_overexpression)
                                                                      .minus(outside_overexpression)
                                                                      .minus(outside_knockout))

    if control_max_size is not None:
        max_perturbation_space = stg.empty_colored_vertices()
        for i in range(control_max_size):
            for perturbed in it.combinations(stg.network().variables(), i):
                for ordering in range(2 ** len(perturbed)):
                    fixes = []
                    fix_space = stg.unit_colored_vertices()
                    for var_id in perturbed:
                        oe_par_name = parameter_names_generator.get_over_expression_from_var(stg.network(), var_id)
                        ko_par_name = parameter_names_generator.get_knockout_from_var(stg.network(), var_id)
                        fix = oe_par_name if ordering % 2 == 0 else ko_par_name
                        ordering //= 2
                        fixes.append(fix)
                        fix_space = fix_space.intersect_colors(stg.fix_parameter(fix, True))
                    max_perturbation_space = max_perturbation_space.union(fix_space)
    else:
        max_perturbation_space = stg.unit_colored_vertices()

    print('Ending space restricting', str(datetime.datetime.now()))

    # Find attractors outside the phenotype (spurious attractors)
    phenotype_violating_space = (stg.unit_colored_vertices()
                                    .intersect(max_perturbation_space)
                                    .minus(phenotype_compliant_space)
                                    .minus(perturbations_violating_space))
    # attractors = my_find_attractors(stg, phenotype_violating_space)
    # spurious_attractors = ba.FixedPoints.symbolic(stg, phenotype_violating_space)
    spurious_attractors = my_find_attractors(stg, phenotype_violating_space)

    # The params (colours x perturbations) which do not violate the phenotype are OK
    return stg.unit_colors().minus(spurious_attractors.colors())
