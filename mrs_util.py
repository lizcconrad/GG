# contains helper functions for composing MRS and generating from MRS
# ORGANIZED: Y (01/04/2023)
# DOCUMENTED: Y (01/04/2023)
import config
from delphin import ace, mrs
from delphin.codecs import simplemrs
import mrs_algebra


def check_if_quantified(check_ssement):
    """
    Check if the given SSEMENT is quantified (assumes generation is occurring on referring expressions)
    :param check_ssement: SSEMENT to be checked
    :type check_ssement: SSEMENT
    :return: quantified SSEMENT (may be unchanged from given)
    :rtype: SSEMENT
    """
    # if the INDEX is not the ARG0 of something with RSTR, gg
    index = check_ssement.index
    for rel in check_ssement.rels:
        if rel.args['ARG0'] == index and 'RSTR' in rel.args:
            return True
        else:
            return False


def wrap_with_quantifier(unquant_ssement):
    """
    Wrap the given SSEMENT in a quantifier
    :param unquant_ssement: unquantified SSEMENT
    :type unquant_ssement: SSEMENT
    :return: quantified SSEMENT
    :rtype: SSEMENT
    """
    # just using 'the' for now
    quant = mrs_algebra.create_base_SSEMENT('_the_q')
    return mrs_algebra.op_scopal(quant, unquant_ssement)


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


def get_most_specified_variable(eq_vars):
    """
    Get the most "specific" variable to serve as the representative for the EQ set
    That is, a variable of type x is more specific than one of type i, according to the ERG hierarchy
    :param eq_vars: list of variables that are equivalent
    :type eq_vars: list
    :return: most specific variable
    :rtype: str
    """
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
            new_seps.append(mrs_algebra.SEP(r.predicate, new_r_label, new_r_args))


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
    return mrs_algebra.SSEMENT(newest_top, newest_ltop, newest_index, current_seps, current_variables, current_ssement.holes, None, new_hcons)


def wrap_and_generate(final_ssement):
    """
    Wraps a refex with the "unknown" predicate, which the ERG requires for generation, then performs the generation
    :param final_ssement: SSEMENT to wrap
    :type final_ssement: SSEMENT
    """
    # quantify if not already quantified
    if check_if_quantified(final_ssement):
        quant_final_ssement = final_ssement
    else:
        quant_final_ssement = wrap_with_quantifier(final_ssement)

    # wrap with 'unknown' and overwrite EQs
    unknown = mrs_algebra.create_base_SSEMENT('unknown')
    wrapped_ssement = mrs_algebra.op_final(unknown, quant_final_ssement, mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = overwrite_eqs(wrapped_ssement)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    with ace.ACEGenerator(config.ERG, ['-r', 'root_frag']) as generator:
        print(generate_mrs_string)
        response = generator.interact(generate_mrs_string)
        print("GENERATED RESULTS ... ")
        for r in response.results():
            print(r.get('surface'))
