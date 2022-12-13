from typing import Dict
import biodivine_aeon as ba

from perturbed_graph import PerturbedGraph


def permanent_control(pg: PerturbedGraph, phenotype: Dict[str, bool]):
    stg = pg.get_perturbed_stg()

    phenotype_compliant_space = stg.unit_colored_vertices()
    for var, val in phenotype.items():
        var_id = stg.network().find_variable(var)
        fix = stg.fix_variable(var_id, val)
        phenotype_compliant_space = phenotype_compliant_space.intersect(fix)

    attractors = ba.find_attractors(stg)
    all_attractors = stg.empty_colored_vertices()
    for a in attractors:
        all_attractors = all_attractors.union(a)

    # Find attractors violating the phenotype
    spurious_attractors = all_attractors.minus(phenotype_compliant_space)

    # The params (colours x perturbations) which do not violate the phenotype are OK
    return stg.unit_colors().minus(spurious_attractors.colors())
