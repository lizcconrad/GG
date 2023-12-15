# Contains functions for building graphs and writing them to files
# ORGANIZED: Y (08/28/2023)
# DOCUMENTED: Y (08/28/2023)
import networkx as nx


# TODO: Needs to be generalized for data shapes beyond the perplexity data
def build_graph(entities):
    """
    build a graph out of a list of entities where nodes are entities and property values,
    and edges are relationships between entities and property names

    Data shape:
    {'Entity': 'idGlowingGrass1',
        'Properties': [
            {'args': ['idGlowingGrass1_prop_idColor', 'green'], 'functor': ','}
        ],
        'Relationships': [
            {'args': ['idGlowingGrass1', {'args': ['isTouching', 'idGlowingArea1'
        ], 'functor': ','}],
    'functor': ','}]}

    :param entities: list of entities to build a graph from
    :type entities: list
    """
    # if entities is not already a list, make it one
    if not isinstance(entities, list):
        entities = [entities]

    # create the graph
    graph = nx.DiGraph()

    for entity in entities:
        # add a node for the entity ...
        entity_name = entity['Entity']
        graph.add_node(entity_name)

        # add nodes/edges for each property ...
        properties = entity['Properties']
        for prop in properties:
            prop_name = prop['args'][0]
            prop_value = prop['args'][1]
            graph.add_edge(entity_name, prop_value, label=prop_name)

        # add edges for relationships between entities...
        relationships = entity['Relationships']
        for rel in relationships:
            rel_name = rel['args'][1]['args'][0]
            other_entity = rel['args'][1]['args'][1]
            graph.add_edge(entity_name, other_entity, label=rel_name)

    return graph


def write_graph_to_dot(graph, filepath):
    """
    write the graph to a .dot file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    nx.nx_pydot.write_dot(graph, filepath)


def write_graph_to_png(graph, filepath):
    """
    write the graph to a .png file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    png_graph = nx.drawing.nx_pydot.to_pydot(graph)
    png_graph.write_png(filepath)


def write_graph_to_svg(graph, filepath):
    """
    write the graph to a .svg file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    png_graph = nx.drawing.nx_pydot.to_pydot(graph)
    png_graph.write_svg(filepath)











