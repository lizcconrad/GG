# CONVERTING GRAPH TO MRS
# ORGANIZED: Y (01/04/2023)
# DOCUMENTED: Y (01/04/2023)
import json
import re
import random
import data_regularization
import composition_library

# TODO: graph selection? based on complexity? offload to graph_util.py perhaps

# dict of composition functions and their composition types
# VALUES:
#   PARENT_HOLE: parent (hole) -> hole (plug) ... photos --(of)--> cake
#   PARENT_PLUG: parent (plug) -> child (hole) ... apple --(color)--> red
#   EDGE_PRED_PARENT_CHILD: parent (ARG1) -> child (ARG2) + edge predicate ... cookie --(on)--> plate
COMPOSITION_TYPES = json.load(open("comp_to_graph_relations.json"))


def load_lexicon(lexicon_filename):
    """
    Load the lexicon given a filename
    :param lexicon_filename: filename fo the lexicon
    :type lexicon_filename: str
    :return: lexicon in json format
    :rtype: dict
    """
    lexicon_file = open(lexicon_filename)
    lexicon = json.load(lexicon_file)
    return lexicon


def guess_pos_and_create_ssement(pred_label, variables={}):
    """
    Given a predicate label, guess the part of speech and then generate the basic SSEMENT
    :param pred_label: predicate label
    :type pred_label: str
    :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
    :type variables: dict
    :return: basic SSEMENT
    :rtype: SSEMENT
    """
    # noun
    if re.match('_[A-z]+_n_[0-9]$', pred_label):
        return composition_library.noun_ssement(pred_label, variables)
    # adjective
    elif re.match('_[A-z]+_a_[0-9]$', pred_label):
        return composition_library.adjective_ssement(pred_label, variables)
    # verb
    elif re.match('_[A-z]+_v_[0-9]$', pred_label):
        return composition_library.verb_ssement(pred_label, variables)
    # quantifier
    elif re.match('_[A-z]+_q$', pred_label):
        return composition_library.quant_ssement(pred_label, variables)
    # preposition
    elif re.match('_[A-z]+_p(_loc)*$', pred_label):
        return composition_library.preposition_ssement(pred_label, variables)
    # if no guess, do basic_ssement, assuming ARG0 as INDEX
    else:
        return composition_library.basic(pred_label, variables)



def parent_hole_composition(parent, child, edge_rule):
    """
    Parent MRS has a hole plugged by the child, edge introduces no predicate
    ex. photos of cupcakes
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_rule: edge text
    :type edge_rule: str
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # get the composition rule from the lexicon via the edge name
    comp_rule = getattr(composition_library, edge_rule)
    # when the child is the plug, the parent is the functor, so it goes first
    # e.g. adjective(adj, nom)
    return comp_rule(parent, child)


def parent_plug_composition(parent, child, edge_rule):
    """
    Parent MRS has is the plug for the hole in the child MRS, edge introduces no predicate
    ex. red apple
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_rule: edge text
    :type edge_rule: str
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # get the composition rule from the lexicon via the edge name
    comp_rule = getattr(composition_library, edge_rule)
    # when the parent is the plug, the child is the functor, so it goes first
    # e.g. adjective(adj, nom)
    return comp_rule(child, parent)


def edge_predicate(parent, child, edge_json):
    """
    Edge introduces its own predicate, parent serves as ARG1, child serves as ARG2
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_json: json containing edge information
    :type edge_json: dict
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # if an edge introduces a predicate, then the json info for the edge will look like this:
    # {edge}: {
    #   "composition": {...},
    #   {predicate_type}: {...}
    # so the edge_pred being introduced is whatever the value of that second property is
    # and the composition rule is the value of the "composition" property
    comp_rule_name = edge_json["composition"]
    comp_rule = getattr(composition_library, comp_rule_name)
    # edge pred information
    edge_pred = edge_json["property_predicate"]["predicate_label"]
    edge_ssement_type = edge_json["property_predicate"]["predicate_type"]
    edge_ssement_rule = getattr(composition_library, edge_ssement_type)
    edge_ssement = edge_ssement_rule(edge_pred)
    return comp_rule(edge_ssement, parent, child)


# get the MRS for an individual node
def node_to_mrs(node, lexicon, variables={}):
    """
    Create MRS for individual node
    :param node: node text
    :type node: str
    :param lexicon: lexicon with node to ERG predicate label mappings
    :type lexicon: dict
    :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
    :type variables: dict
    :return: SSEMENT for the node
    :rtype: SSEMENT
    """
    # get ERG predicate
    # might involve compounds or synonyms

    # see if it's a node that's categorized as an entityType
    try:
        node_json = lexicon['entityTypes'][node]
    except KeyError:
        # see if it's a propertyValue
        try:
            node_json = lexicon['propertyValues'][node]
        except KeyError:
            raise KeyError("Can't find '{}' as a key in the lexicon".format(node))

    # if it's just a string, return the ssement for the pred label
    if isinstance(node_json, str):
        return guess_pos_and_create_ssement(node_json, variables)
    else:
        if node_json['composition'] == 'compound':
            head = guess_pos_and_create_ssement(node_json['predicates']['head'], variables)
            nonhead = guess_pos_and_create_ssement(node_json['predicates']['modifier'])
            return composition_library.compound(head, nonhead)
        # TODO: this is here but it's not going to be used for GP2 because it's too hard to evaluate
        #  as in ... i need to get every possible synonym to express the variety for one node
        #  but as it stands now I return one (1) MRS per graph
        elif node_json['composition'] == 'synonyms':
            syn_choice = random.choice(node_json['predicates'])
            return guess_pos_and_create_ssement(syn_choice, variables)


def edge_to_mrs(parent, child, edge, lexicon):
    """
    Compose MRS between parent and child, considering any semantic contribution made by the edge
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge: edge text
    :type edge: str
    :param lexicon: lexicon with node to ERG predicate label mappings
    :type lexicon: dict
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    edge_json = lexicon['properties'][edge]
    # assume edge name in lexicon is direct composition type
    # e.g. "idColor": "adjective"
    # otherwise, get the "composition" value
    if isinstance(edge_json, str):
        edge_composition = edge_json
    else:
        edge_composition = lexicon['properties'][edge]['composition']

    composition_type = COMPOSITION_TYPES[edge_composition]
    if composition_type == 'PARENT_HOLE':
        return parent_hole_composition(parent, child, edge_json)
    elif composition_type == 'PARENT_PLUG':
        return parent_plug_composition(parent, child, edge_json)
    elif composition_type == 'EDGE_PRED_PARENT_CHILD':
        return edge_predicate(parent, child, edge_json)


def graph_to_mrs(root, graph, lexicon, variables={}):
    """
    Convert a graph to MRS (SSEMENT)
    :param root: text on root node
    :type root: str
    :param graph: graph to compose MRS from
    :type graph: DiGraph
    :param lexicon: lexicon with node to ERG predicate label mappings
    :type lexicon: dict
    :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
    :type variables: dict
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    regularized_root = data_regularization.regularize_node(root)

    # 1. get MRS for root
    root_mrs = node_to_mrs(regularized_root, lexicon, variables)

    # 2. for each child ...
    new_composed_mrs = root_mrs
    for child in graph.successors(root):
        # 3. recurse and get the full MRS for the child
        child_mrs = graph_to_mrs(child, graph, lexicon)
        # 4. compose child_mrs with the root
        edge = graph.get_edge_data(root, child)
        new_composed_mrs = edge_to_mrs(new_composed_mrs, child_mrs, data_regularization.regularize_edge(edge[0]['label']), lexicon)

    # 5. return the result
    return new_composed_mrs


