import mrs_algebra
import composition_library
from delphin import ace, mrs
from delphin.codecs import simplemrs


# wrap with the 'unknown' predicate and generate
def wrap_and_generate(final_ssement):
    unknown = mrs_algebra.create_base_SSEMENT('unknown')
    wrapped_ssement = mrs_algebra.op_final(unknown, final_ssement, mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = mrs_algebra.overwrite_eqs(wrapped_ssement)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    with ace.ACEGenerator('../ERG/erg-2020.dat', ['-r', 'root_frag']) as generator:
        print(generate_mrs_string)
        response = generator.interact(generate_mrs_string)
        print("GENERATED RESULTS ... ")
        for r in response.results():
            print(r.get('surface'))


# "the red apple"
def adjective_example():
    print("-- ADJECTIVE -- ")
    apple = composition_library.noun_ssement('_apple_n_1')
    red = composition_library.adjective_ssement('_red_a_1')
    a = composition_library.quant_ssement('_a_q')
    adjective_uquant = composition_library.adjective(red, apple)
    adjective_quant = composition_library.quantify(a, adjective_uquant)

    wrap_and_generate(adjective_quant)


# "a lake east of the mountains"
def relative_direction_example():
    print("--- RELATIVE DIRECTION --- ")

    mountain = composition_library.noun_ssement('_mountain_n_1')
    the = composition_library.quant_ssement('_the_q')
    ground_ssement = composition_library.quantify(the, mountain)

    figure_ssement = composition_library.noun_ssement('_lake_n_1')

    east = composition_library.adjective_ssement('_east_a_1')

    unquant_relative_dir = composition_library.relative_direction(east, figure_ssement, ground_ssement)

    a = composition_library.quant_ssement('_a_q')

    quant_relative_dir = composition_library.quantify(a, unquant_relative_dir)

    wrap_and_generate(quant_relative_dir)


# "the trash can"
def compound_example_one_node():
    print("--- COMPOUND ---")

    head_ssement = composition_library.noun_ssement('_can_n_1')
    non_head_ssement = composition_library.noun_ssement('_trash_n_1')
    compound_unquant = composition_library.compound(head_ssement, non_head_ssement)

    the = composition_library.quant_ssement('_the_q')

    compound_quant = composition_library.quantify(the, compound_unquant)

    wrap_and_generate(compound_quant)


# "the north room"
# TODO: have to fix the fact that it gets the wrong _wall_n_of synopsis
def compound_example_two_nodes():
    print("--- RELATIONAL COMPOUND ---")

    head_ssement = composition_library.noun_ssement('_room_n_unit')
    non_head_ssement = composition_library.noun_ssement('_north_n_of')
    compound_unquant = composition_library.compound(head_ssement, non_head_ssement)

    the = composition_library.basic('_the_q')

    compound_quant = composition_library.quantify(the, compound_unquant)

    wrap_and_generate(compound_quant)


# "the mirror above the sink"
def above_example():
    print("-- ABOVE -- ")
    non_head_ssement = composition_library.noun_ssement('_sink_n_1')
    the_1 = composition_library.quant_ssement('_the_q')
    non_head_quant = composition_library.quantify(the_1, non_head_ssement)

    head_ssement = composition_library.noun_ssement('_mirror_n_1')

    above_ssement = composition_library.preposition_ssement('_above_p')

    above = composition_library.preposition(above_ssement, head_ssement, non_head_quant)

    the_2 = composition_library.quant_ssement('_the_q')

    above_quant = composition_library.quantify(the_2, above)

    wrap_and_generate(above_quant)


# "the bottle next to the bowl"
def next_to_example():
    print("-- NEXT TO -- ")
    non_head_ssement = composition_library.noun_ssement('_bowl_n_1')
    the_1 = composition_library.quant_ssement('_the_q')
    non_head_quant = composition_library.quantify(the_1, non_head_ssement)

    head_ssement = composition_library.noun_ssement('_bottle_n_of')

    nextto_ssement = composition_library.preposition_ssement('_next+to_p')

    nextto = composition_library.preposition(nextto_ssement, head_ssement, non_head_quant)

    the_2 = composition_library.quant_ssement('_the_q')

    above_quant = composition_library.quantify(the_2, nextto)

    wrap_and_generate(above_quant)


# "the lemon scented soap"
def past_participle_example():
    print("-- PAST PARTICIPLE --")

    the = composition_library.quant_ssement('_the_q')
    lemon = composition_library.noun_ssement('_lemon_a_1')
    scented = composition_library.verb_ssement('_scent_v_1')
    udef_q = composition_library.quant_ssement('udef_q')
    soap = composition_library.noun_ssement('_soap_n_1')

    udef_soap = composition_library.quantify(udef_q, soap)
    scented_arg2 = mrs_algebra.op_non_scopal_lbl_unshared(scented, udef_soap, 'ARG2')
    scented_arg1 = mrs_algebra.op_non_scopal_lbl_unshared(scented_arg2, lemon, 'ARG1')
    quant_secnted = composition_library.quantify(the, scented_arg1)

    wrap_and_generate(quant_secnted)


def main():
    example_functions = [compound_example_one_node, compound_example_two_nodes, relative_direction_example,
                         above_example, adjective_example, next_to_example]
    for ex in example_functions:
        ex()
        print("\n\n")

if __name__ == "__main__":
    main()
