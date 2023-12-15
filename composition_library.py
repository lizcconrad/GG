# File that contains various common forms of composition, refer to the function names here in your lexicon file?
from mrs_algebra import create_base_SSEMENT, op_scopal, op_non_scopal_lbl_shared, op_non_scopal_lbl_unshared


# ENTITY FUNCTIONS
# basic node
# this kind of does nothing?
# but i want the graph-to-MRS alg to only refer to the comp library
# so this is a wrapper for the most basic case
def basic(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def noun_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def adjective_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def verb_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def quant_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def preposition_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# SINGULAR NODE
# i have "compound" for both entities and relationships
# some individual nodes just are a compound
# but some nodes have a relationship that warrants a compound
# so the graph-to-MRS to alg will just have to call the basic() fxn before using this for the single node case
# or build each node and then use this as the composition
def compound(head_ssement, nonhead_ssement):
    udef = create_base_SSEMENT('udef_q')
    udef_nonhead = op_scopal(udef, nonhead_ssement)

    compound_ssement = create_base_SSEMENT('compound', {}, 'ARG1')
    compound_ARG2 = op_non_scopal_lbl_unshared(compound_ssement, udef_nonhead, 'ARG2')

    compound_final = op_non_scopal_lbl_shared(compound_ARG2, head_ssement, 'ARG1')
    return compound_final


# COMPOSITION FUNCTIONS
def quantify(quant_ssement, unquant_ssement):
    return op_scopal(quant_ssement, unquant_ssement)


def adjective(adj_ssement, nom_ssement):
    return op_non_scopal_lbl_shared(adj_ssement, nom_ssement, 'ARG1')


def preposition(prep_ssement, head_ssement, nonhead_ssement):
    preposition_ARG2 = op_non_scopal_lbl_unshared(prep_ssement, nonhead_ssement, 'ARG2')
    preposition_ARG1 = op_non_scopal_lbl_shared(preposition_ARG2, head_ssement, 'ARG1')
    return preposition_ARG1


# TODO ???
def propertied():
    print("teehee")


# X is east of Y
def relative_direction(direction_ssement, figure_ssement, ground_ssement):
    # figure ssement must be unquantified
    # ground ssement must be quantified

    # create base SSEMENTs for direction and place_n
    place = create_base_SSEMENT('place_n')

    # plug ARG2 of the direction predicate with the thing primary_ssement is directionally relative to
    direction_ARG2_plugged = op_non_scopal_lbl_unshared(direction_ssement, ground_ssement, 'ARG2')

    # plug ARG1 of direction predicate with place_n
    direction_place = op_non_scopal_lbl_shared(direction_ARG2_plugged, place, 'ARG1')

    # use implicit quantifier for SSEMENT thus far
    def_imp = create_base_SSEMENT('def_implicit_q')
    def_imp_direction_place = op_scopal(def_imp, direction_place)

    # create loc_nonsp SSEMENT and plug ARG1 with primary_ssement
    loc_nonsp = create_base_SSEMENT('loc_nonsp', {}, 'ARG1')
    loc_nonsp_ARG1_plugged = op_non_scopal_lbl_shared(loc_nonsp, figure_ssement, 'ARG1')

    # plug ARG2 of loc_nonsp with the direction+relative SSEMENT
    final_dir = op_non_scopal_lbl_unshared(loc_nonsp_ARG1_plugged, def_imp_direction_place, 'ARG2')

    return final_dir



