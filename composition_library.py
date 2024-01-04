# File that contains various common forms of composition, refer to the function names here in your lexicon file
# ORGANIZED: Y (01/04/2023)
# DOCUMENTED: Y (01/04/2023)
from mrs_algebra import create_base_SSEMENT, op_scopal, op_non_scopal_lbl_shared, op_non_scopal_lbl_unshared
import mrs_util


# ENTITY FUNCTIONS
# Each of these simply passes the information to `mrs_algebra.create_base_SSEMENT`,
# but they serve as wrappers because the graph-to-MRS algorithm, and the user's lexicon,
# should only refer to things in composition_library, not the mrs_algebra directly.
def basic(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def noun_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of an adjective is the thing it modifies,
# which is typically what we want as the semantic index after composition with an adjective
def adjective_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def verb_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def quant_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of a preposition is the thing the preposition modifies,
# which is typically what we want as the semantic index after composition with a preposition
def preposition_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# COMPOSITION FUNCTIONS
def compound(head_ssement, nonhead_ssement):
    udef = create_base_SSEMENT('udef_q')
    udef_nonhead = op_scopal(udef, nonhead_ssement)

    compound_ssement = create_base_SSEMENT('compound', {}, 'ARG1')
    compound_ARG2 = op_non_scopal_lbl_unshared(compound_ssement, udef_nonhead, 'ARG2')

    compound_final = op_non_scopal_lbl_shared(compound_ARG2, head_ssement, 'ARG1')
    return compound_final


def quantify(quant_ssement, unquant_ssement):
    return op_scopal(quant_ssement, unquant_ssement)


def adjective(adj_ssement, nom_ssement):
    return op_non_scopal_lbl_shared(adj_ssement, nom_ssement, 'ARG1')


def preposition(prep_ssement, head_ssement, nonhead_ssement):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not mrs_util.check_if_quantified(nonhead_ssement):
        quant_nonhead_ssement = mrs_util.wrap_with_quantifier(nonhead_ssement)
    else:
        quant_nonhead_ssement = nonhead_ssement

    preposition_ARG2 = op_non_scopal_lbl_unshared(prep_ssement, quant_nonhead_ssement, 'ARG2')
    preposition_ARG1 = op_non_scopal_lbl_shared(preposition_ARG2, head_ssement, 'ARG1')
    return preposition_ARG1


# TODO ???
def propertied():
    print("teehee")


# X is east of Y
def relative_direction(direction_ssement, figure_ssement, ground_ssement):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not mrs_util.check_if_quantified(ground_ssement):
        quant_ground_ssement = mrs_util.wrap_with_quantifier(ground_ssement)
    else:
        quant_ground_ssement = ground_ssement

    # figure ssement must be unquantified
    # ground ssement must be quantified

    # create base SSEMENTs for direction and place_n
    place = create_base_SSEMENT('place_n')

    # plug ARG2 of the direction_ssement with ground_ssement (i.e. what figure_ssement is directionally relative to)
    direction_ARG2_plugged = op_non_scopal_lbl_unshared(direction_ssement, quant_ground_ssement, 'ARG2')

    # plug ARG1 of direction_ssement with place_n
    direction_place = op_non_scopal_lbl_shared(direction_ARG2_plugged, place, 'ARG1')

    # use implicit quantifier for SSEMENT thus far
    def_imp = create_base_SSEMENT('def_implicit_q')
    def_imp_direction_place = op_scopal(def_imp, direction_place)

    # create loc_nonsp SSEMENT and plug ARG1 with figure_ssement
    loc_nonsp = create_base_SSEMENT('loc_nonsp', {}, 'ARG1')
    loc_nonsp_ARG1_plugged = op_non_scopal_lbl_shared(loc_nonsp, figure_ssement, 'ARG1')

    # plug ARG2 of loc_nonsp with the direction+relative SSEMENT
    final_dir = op_non_scopal_lbl_unshared(loc_nonsp_ARG1_plugged, def_imp_direction_place, 'ARG2')

    return final_dir



