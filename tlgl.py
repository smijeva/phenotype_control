import biodivine_aeon as ba
from control import permanent_control
from perturbed_graph import PerturbedGraph
from datetime import datetime


with open('case_study/tlgl.aeon') as handle:
    content = handle.read()
bn = ba.BooleanNetwork.from_aeon(content)
vars = bn.variables()
rg = bn.graph()
sag = ba.SymbolicAsyncGraph(bn)
sag.unit_colors().cardinality()

rg = bn.graph()
sag = ba.SymbolicAsyncGraph(bn)
sag.unit_colors().cardinality()
start = datetime.now()
ss = ba.FixedPoints.symbolic(sag, sag.unit_colored_vertices())
print(ss)
print(datetime.now()-start)
vars = bn.variables()
rg = bn.graph()
print('creating pg')
pg = PerturbedGraph(bn,
                    ["v_SPK1", "v_S1P", "v_PDGFR", "v_PI3K", "v_JAK", "v_RAS", "v_NFk", "v_MEK", "v_ERK"],
                    ["v_DISC", "v_Ceramide", "v_Caspase", "v_SOCS", "v_GAP"])
print("starting control")
start = datetime.now()
permanent_control(pg, {"v_Apoptosis": False}, 1)
end = datetime.now()
print(f'permanent control {end - start}')