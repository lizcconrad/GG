# Contains examples of MRS composition using functions from the composition library
# ORGANIZED: Y (01/04/2023)
# DOCUMENTED: Y (01/04/2023)
import mrs_algebra
import composition_library
from mrs_util import wrap_and_generate


# "a red apple"
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
# TODO: have to fix the fact that it gets the wrong _wall_n_of synopsis, using _room_n_unit for now in its place
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
    print("-- ABOVE --")
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
    print("-- NEXT TO --")
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
# TODO: ... this works but it's bizarre, possibly because of the MRS structure I chose to model after
def propertied_example():
    print("-- PAST PARTICIPLE --")

    the = composition_library.quant_ssement('_the_q')
    lemon = composition_library.adjective_ssement('_lemon_a_1')
    scented = composition_library.verb_ssement('_scent_v_1', {}, 'ARG2')
    soap = composition_library.noun_ssement('_soap_n_1')

    lemon_soap = composition_library.adjective(lemon, soap)
    lemon_scented_soap = mrs_algebra.op_non_scopal_lbl_shared(scented, lemon_soap, 'ARG2')
    the_lemon_scented_soap = composition_library.quantify(the, lemon_scented_soap)

    wrap_and_generate(the_lemon_scented_soap)


def main():
    example_functions = [compound_example_one_node, compound_example_two_nodes, relative_direction_example,
                         above_example, adjective_example, next_to_example, propertied_example]
    for ex in example_functions:
        ex()
        print("\n\n")


if __name__ == "__main__":
    main()
