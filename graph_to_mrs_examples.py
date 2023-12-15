import config
import graph_to_mrs
import composition_library
import generator_util


lexicon = graph_to_mrs.load_lexicon(config.LEXICON)


# TODO: make the micrograph lexicon and start testing a graph to mrs algorithm
# apple = composition_library.noun_ssement('_apple_n_1')
# red = composition_library.adjective_ssement('_red_a_1')
#
# table = composition_library.noun_ssement('_table_n_1')
# the = composition_library.quant_ssement('_the_q')
# the_table = composition_library.quantify(the, table)
#
#
# red_apple = graph_to_mrs.parent_plug_composition(apple, red, lexicon['properties']['color'])
# on_table = graph_to_mrs.edge_predicate(red_apple, the_table, lexicon['properties']['isOn'])
#
# quant_test = composition_library.quantify(composition_library.quant_ssement('_the_q'), on_table)
#
# generator_util.wrap_and_generate(quant_test)


# test the node fxn
node_test = graph_to_mrs.node_to_mrs('idPainting', lexicon, {})
generator_util.wrap_and_generate(node_test)