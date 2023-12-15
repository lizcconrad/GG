# taken from the _mrs.py file to test my subclas
from typing import Optional, Iterable, Mapping, Dict
from delphin.lnk import Lnk
from delphin import variable
from delphin import sembase
from delphin import scope
# end from _mrs.py

import config
from delphin import ace, mrs, semi
from delphin.codecs import simplemrs


class VarIterator:
    """
    Iterator to help with creating handles, indices, and variables in SSEMENTs
    """
    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        next_num = self.count
        self.count += 1
        return next_num


class VarLabeler:
    """
    Returns the appropriate label for the next created handle, index, or variable
    """
    def __init__(self):
        # make a varIterator for the numbers on the variables
        self.varIt = iter(VarIterator())

    def get_var_name(self, var_type):
        return "{}{}".format(var_type, next(self.varIt))


class SEP(mrs.EP):
    """
    subclass of the PyDelphin EP object for an SEP
    Formally, an EP is a tuple of the form <LBL, REL, ARGS, SC-ARGS>
        - LBL -- handle which is the label of the eP
        - REL -- relation (i.e. predicate)
        - ARGS -- list of zero or more ordinary variable arguments
        - SC-ARGS -- list of zero or more handles corresponding to scopal arguments
    In PyDelphin, an EP contains all of those parts except that the ARGS and SC-ARGS list is collapsed into one

    An SEP is a tuple of the exact same form, so realistically this class might not be needed,
    but in keeping with the algebra I kept it for now
    """

    def __init__(self,
                 predicate: str,
                 label: str,
                 args: Optional[Dict[str, str]] = None,
                 lnk: Optional[Lnk] = None,
                 surface=None,
                 base=None):
        super().__init__(predicate, label, args, lnk, surface, base)


class SSEMENT(mrs.MRS):
    """
    Wrapper class for the PyDelphin MRS object.
    An MRS is a tuple of the form <Hook, R, C> where...
        ... Hook is a tuple of the form <GT, Ind, Xarg> where ...
            ... GT is the top handle
            ... Index is the index
            ... Xarg is ... ? used to deal with raising/control constructions
        ... R is a bag of EPs (see the EP class for details)
        ... C is a bag of handle constraints

    However, a SSEMENT has additional information, namely the holes. It is a tuple of the form <Hook, Holes, Lzt, Eqs, Hcons> where ...
        ... Hook is a tuple of the form <GT, Ind, Xarg> (same as above)
        ... Holes is the list of holes
        ... Lzt is the list of SEPs (analogous to R in an MRS)
        ... Eqs is a list of equalities between variables
        ... Hcons is a bag of handle constraints
    Basically, the only thing SSEMENT has that MRS does not is Holes, so I'm creating an object that uses
    the PyDelphin MRS object and points to pieces of it, but also has Holes
    """

    # TODO: hcons and icons are of type mrs.HCons and mrs.ICons ... should just be HCons but this isn't in the real file yet
    def __init__(self,
                 top: Optional[str] = None,
                 ltop: Optional[str] = None,
                 index: Optional[str] = None,
                 rels: Optional[Iterable[SEP]] = None,
                 variables: Optional[Mapping[str, Mapping[str, str]]] = None,
                 holes: Optional[Mapping[str, Mapping[str, str]]] = None,
                 eqs: Optional[Iterable[tuple[str, ...]]] = None,
                 hcons: Optional[Iterable[mrs.HCons]] = None,
                 icons: Optional[Iterable[mrs.ICons]] = None,
                 lnk: Optional[Lnk] = None,
                 surface=None,
                 identifier=None):

        # top is GTOP, probably leaving it empty in most cases until the final MRS
        super().__init__(top, index, rels, hcons, icons, variables, lnk, surface, identifier)

        # LTOP appropriate for composition
        self.ltop = ltop
        self.holes = holes
        self.eqs = eqs


# global variable labeler for creating new SSEMENTS
# might not want to keep this here, not sure where to instantiate it
SEMI = semi.load(config.SEMI)
VAR_LABELER = VarLabeler()

# need a way to specify which argument gets chosen as the INDEX . . .
SEMANTIC_TYPES = {

}


def group_equalities(eqs):
    """
    Group equalities from a list of EQs into lists as opposed to individual equalities
    That is, if x1=x2 and x2=x3 create a list [x1, x2, x3] such that they're in an equality "group"
    :param eqs: List of eqs
    :type eqs: list
    :return: new_sets, list of EQ groups
    :rtype: list
    """
    new_sets = []
    # as long as there are eqs still not covered
    while eqs:
        # pop one eq off the list
        current_eq = eqs.pop()
        # flag for whether a new group is needed
        need_new = True
        # for every set in the list of new_sets,
        for i, new_set in enumerate(new_sets):
            # if either member is in the new_set, update the set so that it's the union of both
            if current_eq[0] in new_set or current_eq[1] in new_set:
                new_sets[i] = new_set.union(set(current_eq))
                # and therefore we don't need to create a new set because we found the right group
                need_new = False
        # we didn't find a match, so start a new group
        if need_new:
            new_sets.append(set(current_eq))

    return new_sets


def get_holes(sep):
    """
    Get the holes contributed by a particular SEP to send into a SSEMENT
    :param sep: SEP object to get holes from
    :type sep: SEP
    """
    holes = {}
    # if it's a quantifier, everything is a hole, EXCEPT BODY
    if sep.is_quantifier():
        for arg in sep.args:
            if arg != 'BODY':
                holes[arg] = sep.args[arg]
    # otherwise, everything except ARG0 is a hole
    else:
        for arg in sep.args:
            if sep.args[arg] != sep.iv:
                holes[arg] = sep.args[arg]
    return holes


def concretize(var_labeler, synopsis):
    """
    Given a synopsis for a predicate, concretize the variable names, e.g. update 'e' to be 'e1', and return args dict
    :param var_labeler: iterator to label variables
    :type var_labeler: VarLabeler object
    :param synopsis: Synopsis of an erg predicate per the SEMI
    :type synopsis: Synopsis object from PyDelphin
    :return: dictionary mapping roles to values
    :rtype: dict
    """
    syn_dict = synopsis.to_dict()
    args_dict = {}
    for role in syn_dict['roles']:
        # currently, role['value'] is just a variable type, like e
        # we still want that in the final variable name, so pass it in as the prefix to the var_labeler
        # but set the value of the role in the args_dict to be the returned var_name (something like e2)
        args_dict[role['name']] = var_labeler.get_var_name(role['value'])

    return args_dict


def get_most_specified_variable(eq_vars):
    # this isn't going to check for incompatibilities, I'm assuming those have been handled already
    types = {
        'u': 0,
        'i': 1,
        'p': 1,
        'e': 2,
        'x': 2,
        'h': 2
    }

    most_spec_var = eq_vars[0]
    for var in eq_vars:
        # type is the first char in the string
        # if the type of the current var is more specific than the already chosen one,
        # update the chosen one
        if types[var[0]] > types[most_spec_var[0]]:
            most_spec_var = var
    return most_spec_var


def create_base_SSEMENT(predicate, variables={}, index_arg='ARG0'):
    """
    Make the base case SSEMENT, that is a SSEMENT with only one SEP in it before any composition has occurred
    :param predicate: ERG predicate label
    :type predicate: str
    :param index_arg: which argument of the EP is considered the INDEX
    :type index_arg: str
    :return: new SSEMENT with one SEP in it
    :rtype: SSEMENT
    """

    # the purpose of the index_arg is because some SEPs will want to declare their own INDEX is that of one of their arguments
    # that is, the INDEX of a SSEMENT with just _cute_a_1 should be the ARG1, not ARG0 of the cute sep
    # because _cute_a_1 can be used both as a modifier (want ARG1 as INDEX) and predicatively (want ARG0 as INDEX),
    # this function lets me determine at the time of creating the base SSEMENT what's happening
    # so at the time of starting composition that decision will have to be made somehow

    syn = SEMI.find_synopsis(predicate)
    args = concretize(VAR_LABELER, syn)
    sep = SEP(predicate, VAR_LABELER.get_var_name('h'), args)

    # for variables, assume that the INDEX variable is the one with the passed in properties (e.g. singular)
    return SSEMENT(None, sep.label, sep.args[index_arg], [sep], {sep.args[index_arg]: variables}, get_holes(sep))


def op_non_scopal_lbl_shared(functor, argument, hole_label):
    """
    Non-scopal (intersective) composition where the LBL is shared between SEPs (e.g. adjective modifying a noun)
    :param functor: functor EP, such as an adjective
    :type functor: SSEMENT
    :param argument: argument EP, such as the noun an adjective modifies
    :type argument: SSEMENT
    :param hole_label: Label of the hole being filled, e.g. ARG1
    :type hole_label: str
    :return: composed SSEMENT
    :rtype: SSEMENT
    """

    """Note: I have two non-scopal functions, even though that goes against the algebra slightly
          because it is basically the "lexical entry" that should determine whether the LBL gets identified between two SSEMENTS
          however I'm not working with lexical entries . . . so i need to be able to add an eq between lbls when necessary
          sometimes you need to identify LBLs in non-scopal, sometimes you don't"""

    # FUNC = semantic functor
    # ARG = semantic argument
    # HOLE = hole to be filled on the functor by composition
    # ... result of composition ...
    # hook = FUNC.hook
    # ... hook is the LTOP and the INDEX
    # holes = FUNC.holes + ARG.holes - HOLE
    # seps = FUNC.seps + ARG.seps
    # eqs = tr_closure(FUNC.eqs, ARG.eqs) + eq(ARG.hook, HOLE) + eq(FUNC.ltop, ARG.ltop)
    # ... new EQ between the ARG.hook and the hole being filled, also a new EQ between the FUNC and ARG lbls
    # qeqs = FUNC.qeqs + ARG.qeqs + FUNC.holes[RSTR]=qARG.ltop

    # Variables are not included in the algebra,
    # but I need the ability to specific syntactic properties on certain variables
    # e.g. singular/plural, so there is a dict mapping of variables to properties (which are mapped to values)
    # the new dict at each step of composition is just the union of the dicts from each SSEMENT
    # variables = FUNC.variables + ARG.variables

    # hook
    new_ltop = functor.ltop
    new_index = functor.index

    new_holes = {}

    # EQs ... empty list if there are none
    functor_eqs = [] if functor.eqs is None else functor.eqs
    argument_eqs = [] if argument.eqs is None else argument.eqs

    # QEQs ... empty list if there are none
    functor_qeqs = [] if functor.hcons is None else functor.hcons
    argument_qeqs = [] if argument.hcons is None else argument.hcons

    # add EQs and QEQs together
    new_eqs = functor_eqs + argument_eqs
    new_qeqs = functor_qeqs + argument_qeqs

    for hole in functor.holes:
        # if it's not the labeled hole add it to the new list of holes
        if hole != hole_label:
            new_holes[hole] = functor.holes[hole]
        # otherwise, need to set an EQ between hook(ARG)=hole_arg
        else:
            new_eqs.append((argument.index, functor.holes[hole]))

    # also need to add an eq between the LBL of the functor and argument
    new_eqs.append((functor.ltop, argument.ltop))

    # SEPS
    new_seps = functor.rels + argument.rels

    # Variables
    new_variables = {}
    new_variables.update(functor.variables)
    new_variables.update(argument.variables)

    # None for GTOP, we're not at a final SSEMENT yet
    return SSEMENT(None, new_ltop, new_index, new_seps, new_variables, new_holes, new_eqs, new_qeqs)


def op_non_scopal_lbl_unshared(functor, argument, hole_label):
    """
        Non-scopal (intersective) composition where the LBL is unshared between SEPs (e.g. verb and its complements)
        :param functor: functor EP, such as an adjective
        :type functor: SSEMENT
        :param argument: argument EP, such as the noun an adjective modifies
        :type argument: SSEMENT
        :param hole_label: Label of the hole being filled, e.g. ARG1
        :type hole_label: str
        :return: composed SSEMENT
        :rtype: SSEMENT
        """

    """Note: I have two non-scopal functions, even though that goes against the algebra slightly
          because it is basically the "lexical entry" that should determine whether the LBL gets identified between two SSEMENTS
          however I'm not working with lexical entries . . . so i need to be able to add an eq between lbls when necessary
          sometimes you need to identify LBLs in non-scopal, sometimes you don't"""

    # FUNC = semantic functor
    # ARG = semantic argument
    # HOLE = hole to be filled on the functor by composition
    # ... result of composition ...
    # hook = FUNC.hook
    # ... hook is the LTOP and the INDEX
    # holes = FUNC.holes + ARG.holes - HOLE
    # seps = FUNC.seps + ARG.seps
    # eqs = tr_closure(FUNC.eqs, ARG.eqs) + eq(ARG.hook, HOLE)
    # qeqs = FUNC.qeqs + ARG.qeqs

    # Variables are not included in the algebra,
    # but I need the ability to specific syntactic properties on certain variables
    # e.g. singular/plural, so there is a dict mapping of variables to properties (which are mapped to values)
    # the new dict at each step of composition is just the union of the dicts from each SSEMENT
    # variables = FUNC.variables + ARG.variables

    # hook
    new_ltop = functor.ltop
    new_index = functor.index

    new_holes = {}

    # EQs ... empty list if there are none
    functor_eqs = [] if functor.eqs is None else functor.eqs
    argument_eqs = [] if argument.eqs is None else argument.eqs

    # QEQs ... empty list if there are none
    functor_qeqs = [] if functor.hcons is None else functor.hcons
    argument_qeqs = [] if argument.hcons is None else argument.hcons

    # add EQs and QEQs together
    new_eqs = functor_eqs + argument_eqs
    new_qeqs = functor_qeqs + argument_qeqs

    for hole in functor.holes:
        # if it's not the labeled hole add it to the new list of holes
        if hole != hole_label:
            new_holes[hole] = functor.holes[hole]
        # otherwise, need to set an EQ between hook(ARG)=hole_arg
        else:
            new_eqs.append((argument.index, functor.holes[hole]))

    # SEPS
    new_seps = functor.rels + argument.rels

    # Variables
    new_variables = {}
    new_variables.update(functor.variables)
    new_variables.update(argument.variables)

    # None for GTOP, we're not at a final SSEMENT yet
    return SSEMENT(None, new_ltop, new_index, new_seps, new_variables, new_holes, new_eqs, new_qeqs)


# TODO: add hole_label, like 'believes' ... not just RSTR
def op_scopal(scoping, scoped):
    """
    Scopal composition between SSEMENTS
    :param scoping: Scoping SSEMENT
    :type scoping: SSEMENT
    :param scoped: Scoped SSEMENT
    :type scoped: SSEMENT
    :return: composed SSEMENT
    :rtype: SSEMENT
    """

    # FUNC = semantic functor
    # ARG = semantic argument
    # HOLE = hole to be filled on the functor by composition
    # ... result of composition ...
    # hook = FUNC.hook
    # ... hook is the LTOP and the INDEX
    # holes = FUNC.holes + ARG.holes - HOLE
    # seps = FUNC.seps + ARG.seps
    # eqs = tr_closure(FUNC.eqs, ARG.eqs) + eq(ARG.hook, HOLE)
    # qeqs = FUNC.qeqs + ARG.qeqs + FUNC.holes[RSTR]=qARG.ltop
    # ... new qeq between RSTR of functor and the argument's LTOP

    # Variables are not included in the algebra,
    # but I need the ability to specific syntactic properties on certain variables
    # e.g. singular/plural, so there is a dict mapping of variables to properties (which are mapped to values)
    # the new dict at each step of composition is just the union of the dicts from each SSEMENT
    # variables = FUNC.variables + ARG.variables

    functor = scoping
    argument = scoped

    # ARG0 of a quantifier should be identified with INDEX of scoped_ssement
    hole_label = 'ARG0'

    # hook ... top & index
    new_ltop = functor.ltop
    new_index = functor.index

    new_holes = {}

    # EQs ... empty list if there are none
    functor_eqs = [] if functor.eqs is None else functor.eqs
    argument_eqs = [] if argument.eqs is None else argument.eqs

    # QEQs ... empty list if there are none
    functor_qeqs = [] if functor.hcons is None else functor.hcons
    argument_qeqs = [] if argument.hcons is None else argument.hcons

    # add EQs and QEQs together
    new_eqs = functor_eqs + argument_eqs
    new_qeqs = functor_qeqs + argument_qeqs

    for hole in functor.holes:
        # if it's not the labeled hole add it to the new list of holes
        if hole != hole_label:
            new_holes[hole] = functor.holes[hole]
        # otherwise, need to set an eq btwn hook_arg=hole_arg1
        else:
            # add an eq between the hole of functor and the INDEX of argument
            new_eqs.append((argument.index, functor.holes[hole]))

    # add a qeq between the RESTR of functor and LBL of argument
    new_qeqs.append(mrs.HCons(functor.holes['RSTR'], 'qeq', argument.ltop))

    # seps... union of both
    new_seps = functor.rels + argument.rels

    # Variables
    new_variables = {}
    new_variables.update(functor.variables)
    new_variables.update(argument.variables)

    # None for GTOP, we're not at a final SSEMENT yet
    return SSEMENT(None, new_ltop, new_index, new_seps, new_variables, new_holes, new_eqs, new_qeqs)


def op_final(wrapper_ssement, full_ssement, final_top_label):
    """
    Similar to a scopal operator, a new 'unknown' predicate must be added because the ERG can't generate
    unless the INDEX is of type e, and most refexes have a top INDEX of type x, so a new predicate is added
    and then the GTOP is established as being QEQ to this new predicate
    :param wrapper_ssement:
    :type wrapper_ssement:
    :param full_ssement:
    :type full_ssement:
    :param final_top_label:
    :type final_top_label:
    :return:
    :rtype:
    """

    # FUNC = wrapper_ssement
    # ARG = full_ssement
    # HOLE = hole to be filled on the functor by composition (ARG)
    # ... result of composition ...
    # hook = FUNC.hook
    # ... hook is the LTOP and the INDEX
    # ... a new GTOP variable is now introduced
    # holes = FUNC.holes + ARG.holes - HOLE
    # seps = FUNC.seps + ARG.seps
    # eqs = tr_closure(FUNC.eqs, ARG.eqs) + eq(ARG.hook, HOLE) + eq(FUNC.ltop, ARG.ltop)
    # ... new EQ between the ARG.hook and the hole being filled
    # qeqs = FUNC.qeqs + ARG.qeqs + FUNC.holes[RSTR]=qARG.ltop
    # ... new qeq between RSTR of functor and the argument's LTOP

    functor = wrapper_ssement
    argument = full_ssement

    # ARG of the 'unknown' predicate is identified with the INDEX of the full_ssement
    hole_label = 'ARG'

    # hook ... new GTOP & top & index
    new_top = final_top_label
    new_ltop = functor.ltop
    new_index = functor.index

    new_holes = {}

    # EQs ... empty list if there are none
    functor_eqs = [] if functor.eqs is None else functor.eqs
    argument_eqs = [] if argument.eqs is None else argument.eqs

    # QEQs ... empty list if there are none
    functor_qeqs = [] if functor.hcons is None else functor.hcons
    argument_qeqs = [] if argument.hcons is None else argument.hcons

    # add EQs and QEQs together
    new_eqs = functor_eqs + argument_eqs
    new_qeqs = functor_qeqs + argument_qeqs

    for hole in functor.holes:
        # if it's not the labeled hole add it to the new list of holes
        if hole != hole_label:
            new_holes[hole] = functor.holes[hole]
        # otherwise, need to set an eq btwn hook_arg=hole_arg1
        else:
            # add an eq between the hole of functor and the INDEX of argument
            new_eqs.append((argument.index, functor.holes[hole]))

    # add a qeq between the new GTOP and the LBL on the 'unknown' predicate
    new_qeqs.append(mrs.HCons(final_top_label, 'qeq', functor.ltop))

    # seps... union of both
    new_seps = functor.rels + argument.rels

    # Variables
    new_variables = {}
    new_variables.update(functor.variables)
    new_variables.update(argument.variables)

    return SSEMENT(new_top, new_ltop, new_index, new_seps, new_variables, new_holes, new_eqs, new_qeqs)


def overwrite_eqs(final_ssement):
    """
    Create a new SSEMENT where the EQs have been overwritten to one representative value
    :param final_ssement: final SSEMENT from composition
    :type final_ssement: SSEMENT
    :return: new SSEMENT with overwritten EQs
    :rtype: SSEMENT
    """

    # will be progressively collecting a new list of SEPs, HCONS, and EQs, so start with those from the final_ssement
    # where final_ssement is the SSEMENT that comes out after composition is complete
    current_ssement = final_ssement
    current_seps = current_ssement.rels
    current_variables = current_ssement.variables
    current_hcons = current_ssement.hcons
    # group the equalities so if x1=x2 and x2=x3 there's a list of [x1, x2, x3] with all variables that are equivalent
    grouped_eqs = group_equalities(current_ssement.eqs)

    for eq in grouped_eqs:
        # need to get the more specific variable of the pair
        chosen_var = get_most_specified_variable(list(eq))

        # check the top
        if current_ssement.top in eq:
            newest_top = chosen_var
        else:
            newest_top = current_ssement.top
        # check the ltop
        if current_ssement.ltop in eq:
            newest_ltop = chosen_var
        else:
            newest_ltop = current_ssement.ltop
        # check the index
        if current_ssement.index in eq:
            newest_index = chosen_var
        else:
            newest_index = current_ssement.index

        # check the rels
        new_seps = []
        for r in current_seps:
            if r.label in eq:
                new_r_label = chosen_var
            else:
                new_r_label = r.label
            new_r_args = {}
            for arg in r.args:
                if r.args[arg] in eq:
                    new_r_args[arg] = chosen_var
                else:
                    new_r_args[arg] = r.args[arg]
            new_seps.append(SEP(r.predicate, new_r_label, new_r_args))


        # update the SEP list with the current ones
        current_seps = new_seps

        # update the variable dictionary
        new_variables = {}
        for var in current_variables:
            if var in eq:
                new_variables[chosen_var] = {}
                # update the new property dictionary with properties from every var in the eq group
                for e in eq:
                    new_variables[chosen_var].update(current_variables[e])
            else:
                new_variables[var] = current_variables[var]
        current_variables = new_variables

        # check the hcons...
        new_hcons = []
        for hcon in current_hcons:
            # is there any chance that the hi of an hcon will be one member of an eq
            # and the lo could be another member of the eq? so both need to be checked/changed?
            # idk but i'm scared so
            if hcon.hi in eq:
                new_hi = chosen_var
            else:
                new_hi = hcon.hi
            if hcon.lo in eq:
                new_lo = chosen_var
            else:
                new_lo = hcon.lo
            new_hcons.append(mrs.HCons(new_hi, 'qeq', new_lo))

        current_hcons = new_hcons

        # check the icons...???

    # build new overwritten SSEMENT
    # eqs list is gone
    return SSEMENT(newest_top, newest_ltop, newest_index, current_seps, current_variables, current_ssement.holes, None, new_hcons)