# contains helper functions for composing MRS and generating from MRS
import config
from delphin import ace, mrs
from delphin.codecs import simplemrs
import mrs_algebra


# this assumes we're only ever generating from refexes,
# if it's a full sentence the whole narrative story changes
def check_if_quantified(check_ssement):
    # if the INDEX is not the ARG0 of something with RSTR, gg
    index = check_ssement.index
    for rel in check_ssement.rels:
        if rel.args['ARG0'] == index and 'RSTR' in rel.args:
            return True
        else:
            return False


def wrap_with_quantifier(unquant_ssement):
    # just using 'the' for now
    quant = mrs_algebra.create_base_SSEMENT('_the_q')
    return mrs_algebra.op_scopal(quant, unquant_ssement)


# wraps a refex with the "unknown" predicate which the ERG requires for generation
def wrap_and_generate(final_ssement):
    # quantify if not already quantified
    if check_if_quantified(final_ssement):
        quant_final_ssement = final_ssement
    else:
        quant_final_ssement = wrap_with_quantifier(final_ssement)

    # wrap with 'unknown' and overwrite EQs
    unknown = mrs_algebra.create_base_SSEMENT('unknown')
    wrapped_ssement = mrs_algebra.op_final(unknown, quant_final_ssement, mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = mrs_algebra.overwrite_eqs(wrapped_ssement)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    with ace.ACEGenerator(config.ERG, ['-r', 'root_frag']) as generator:
        print(generate_mrs_string)
        response = generator.interact(generate_mrs_string)
        print("GENERATED RESULTS ... ")
        for r in response.results():
            print(r.get('surface'))
