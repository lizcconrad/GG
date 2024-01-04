import os
import config
import networkx as nx
import graph_to_mrs
import mrs_util

# Load lexicon
lexicon = graph_to_mrs.load_lexicon(config.LEXICON)


# for each graph...
graphdir = "./data/micrograph"
for filename in os.listdir("./data/micrograph"):
    if os.path.splitext(filename)[-1].lower() == '.dot':
        print(os.path.join(graphdir, filename))
        graph = nx.drawing.nx_pydot.read_dot(os.path.join(graphdir, filename))

        # TODO: doesn't work if there are directed cycles, which definitely can happen in a refex graph...
        root = list(nx.topological_sort(graph))[0]

        graphmrs = graph_to_mrs.graph_to_mrs(root, graph, lexicon)
        mrs_util.wrap_and_generate(graphmrs)