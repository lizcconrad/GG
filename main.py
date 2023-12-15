import os
from swiplserver import PrologMQI
from graph_util import build_graph, write_graph_to_dot, write_graph_to_png, write_graph_to_svg

import mrs_algebra
import composition_library
from delphin import ace, mrs
from delphin.codecs import simplemrs

# # set working directory to the directory with the data for the Heal game
# os.chdir("/Users/lizcconrad/Documents/PhD/GP2/perplexity_data/Heal_data/")
#
# # open Prolog thread
# with PrologMQI() as mqi:
#     with mqi.create_thread() as prolog_thread:
#         # consult Debug.pl
#         prolog_thread.query("['Debug.pl']")
#
#         # get all entities with property and relationship data
#         result = prolog_thread.query("getEntityData(Entity, Properties, Relationships).")
#
#
# # go back to current working directory
# os.chdir("/Users/lizcconrad/Documents/PhD/GP2/GG/")
#
# # build graph with all entities
# graph = build_graph(result)
# write_graph_to_dot(graph, "entity_graphs/Heal_TheTrees_entities.dot")
# write_graph_to_png(graph, "entity_graphs/Heal_TheTrees_entities.png")
# write_graph_to_svg(graph, "entity_graphs/Heal_TheTrees_entities.svg")
#
# # then also build one graph for each entity
# for e in result:
#     #  get entity name for file naming
#     name = e['Entity']
#
#     # build graph and save to dot and png
#     g = build_graph([e])
#     write_graph_to_dot(g, "entity_graphs/dot/{}.dot".format(name))
#     write_graph_to_png(g, "entity_graphs/png/{}.png".format(name))
#     write_graph_to_svg(g, "entity_graphs/svg/{}.svg".format(name))

def wrap_and_generate(final_ssement):
    unknown = mrs_algebra.create_base_SSEMENT('unknown')
    wrapped_ssement = mrs_algebra.op_final(unknown, final_ssement, mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = mrs_algebra.overwrite_eqs(wrapped_ssement)

    generate_mrs_string = simplemrs.encode(generate_from)

    with ace.ACEGenerator('../ERG/erg-2020.dat', ['-r', 'root_frag']) as generator:
        print(generate_mrs_string)
        response = generator.interact(generate_mrs_string)
        print("GENERATED RESULTS ... ")
        for r in response.results():
            print(r.get('surface'))


# ... TESTING ZONE ... ##
with ace.ACEParser('../ERG/erg-2020.dat') as parser:
    response = parser.interact("the trash can")
    print(response.result(1)['mrs'])
    cute_mrs = response.result(1).mrs()



the = mrs_algebra.create_base_SSEMENT("_the_q")

var_test = {'NUM': 'sg'}

syn = mrs_algebra.SEMI.find_synopsis("_bird_n_1")
args = mrs_algebra.concretize(mrs_algebra.VAR_LABELER, syn)
sep = mrs_algebra.SEP("_bird_n_1", mrs_algebra.VAR_LABELER.get_var_name('h'), args)
test = mrs_algebra.SSEMENT(None, sep.label, sep.args['ARG0'], [sep], {sep.args['ARG0']: var_test}, mrs_algebra.get_holes(sep))

test_quant = mrs_algebra.op_scopal(the, test)
wrap_and_generate(test_quant)

print("test")