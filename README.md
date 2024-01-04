# README

The Graphical Generator (GG) takes structured nonlinguistic data and generates referring expressions from that data. The expected input of the generator is, therefore, some graph to generate from alongside a lexicon that maps the elements in the graph to predicate labels in the ERG. 

In theory, anybody with graphical representations of their data would only have to create the lexicon to start using the generator, however, in some cases the conversion from data into graphs may be necessary. 

The general pipeline of the project (assuming the data is not in graph form) is as follows:

1. Convert data into a graph
2. Using said graph, use recursive algorithm to traverse the entire thing while composing MRS fragments using the MRS algebra
3. With the full MRS, generate English text using the ERG 

Below is a description of each file in the project, roughly ordered by where they are used in the pipeline. 


## config.py
Allows the user to specify where particular files are located in their setup, e.g. the ERG and their lexicon.

## data_regularization.py
Includes functions to regularize data. Currently based on Perplexity naming conventions. For example, when generating text for an object named idApple1, the graph-to-MRS algorithm will search the algorithm for "idApple1", but really it should be searching for "idApple" because any apple should use the same predicate label for generation, so it should be trimmed when searching the lexicon. 


## graph_util.py
Functions to aid in building graphs from the nonlinguistic structured data. Graph building assumes Perplexity-shaped data. 


## mrs_algebra.py
Contains the functions that implement the MRS algebra as described in Copestake et. al (2001). Technically, in Copestake et. al (2001), the semantic sturctures being used are SSEMENTs (Simple Semantic Elements) and SEPs (Simple Elementary Predications). These are analogous to MRS and EP, respectively. To adhere to the gramamr, this file has `SSEMENT` and `SEP` classes, which are subclasses of `MRS` and `EP` from PyDelphin. 

The file also includes some helper classes (`VarIterator` and `VarLabeler`) which are used to generate the variable values (e.g. `h0`, `x1`) when creating MRSes from scratch. In addition to helper classes, there are helper functions that do some necessary mechanical work:

- `get_holes` -- Find the semantic holes in an SEP
- `concretize` -- Given a synopsis for a predicate label, concretize it to actual variable names. That is, the synopsis for a noun would state that it has an `ARG0` of type `x`, but to actually use that as a predicate in an MRS, there needs to be a concrete variable, e.g. `x1`.

The majority of the code is the functions that implement the algebra:

- `create_base_SSEMENT(predicate, variables={}, index_arg='ARG0')` --  Create a "base" SSEMENT with just one SEP with the given predicate label in the RELS list. You can also provide variable information (e.g. `NUM=sg`) and specify which argument should serve as the semantic index. One time this may need to be changed is with adjectives. According to the algebra, the index of the semantic functor will serve as the index of the composed MRS. In some cases, this requires setting the index of the functor to be identified with something other than `ARG0`. For example, when performing composition with an adjective and a noun, the adjective is the semantic functor, but ultimately it is the index (`ARG0`) of the noun that should be passed up for further composition. Therefore, it is necessary to state that the index of the adjective is identified with its own `ARG1` (which is plugged by the noun's `ARG0`). That way, if the newly composed phrase (e.g. 'red apple') participates in further composition, it is really the index of the noun we are plugging into other things (e.g. '...near the red apple' where we want the index of 'apple', not 'red', to plug the `ARG2` of 'near').
- `op_non_scopal_lbl_shared(functor, argument, hole_label)` -- Perform nonscopal composition and  identify the labels of the functor and the argument (ex. 'red apple').
- `op_non_scopal_lbl_unshared(functor, argument, hole_label)` -- Perform nonscopal composition and don't identify the labels of the functor and the argument (ex. 'in the box')
- `op_scopal(scoping, scoped)` -- Perform scopal composition (ex. 'the apple')
- `op_final(wrapper_ssement, full_ssement, final_top_label)` -- Also not included in the algebra, but the ERG requires that the INDEX of an MRS be of type `e`, which isn't the case with an isolated refex, so it has to be "wrapped" with the `unknown` predicate.  

## composition_library.py
"High level" composition functions that the user's lexicon should refer to. A lot of these are just wrapper functions for things in `mrs_algebra.py`, such as `noun_ssement` which just wraps `create_base_SSEMENT`, however it is more convenient for the user when building the lexicon to say that a particular node label is a noun. The file also includes functions for common composition patterns, such as `adjective` (e.g. using an adjective to modify some nominal), `compound` (e.g. 'trash can'), `preposition`, etc. The user can then say, for example, that `insideOf` is a property that reflects a prepositional relationship. By mapping the user's property to this function in the composition library, the graph-to-MRS algorithm will be able to perform the correct composition. 

## comp_to_graph_relations.json
JSON file that maps each composition function from `composition_library.py` to the shape of relation that type of composition has in a grpah. 

For example, the composition function `noun_ssement` is listed as a `"NODE"` function because a noun is represented in the graph with a node. 

The composition function `adjective` however is represented as `"PARENT_PLUG"`. This is a little opaque, but the idea is that the adjective itself will be contained in a node, and there will be some edge, maybe labelled `"color"` that links the noun being described to the adjective. Typically, such a node will be the parent node, and the ajdective will be the child node. As far as the semantic composition is concerned, the adjective is the semantic functor and the noun is the semantic argument, plugging the hole that the adjective has. Therefore, the parent, i.e. the noun, is the plug, so the composition must be performed such that the child is treated as the functor and the parent is treated as the plug. 

Another possible scenario is one where the edge itself introduces a predicate, this happens with the composition function `preposition` where the composition type is labelled as `"EDGE_PRED_PARENT_CHILD"`. Imagine a parent node labelled `apple` and a child node labelled `box` and the directed edge connecting parent to child is labelled `insideOf`. In this case, the edge introduces the predicate `inside_p`. Additionally, the new predicate takes two arguments, and the "first" one, `ARG1`, is the `apple` in this case and the "second" one `ARG2` is the `box`. So the type is called `EDGE_PRED_PARENT_CHILD` because the edge introduces a predicate and then the parent serves as `ARG1` and the child as `ARG2`. 


## graph_to_mrs.py
Functions to perform the graph to MRS conversion. For every composition type in `comp_to_graph_relations.json` there is a function that performs that type of composition. For example, imagine a graph with a parent node labelled `apple` and a child node labelled `red` and an edge between then named `color`. When composing the MRS, the `graph_to_mrs` function will first start at the root node, `apple` in this case. It will then call `node_to_mrs` which searches the lexicon using the node text. In this hypothetical scenario, we can imagine that the lexicon has a value `apple_n_1` for the key `apple`. It will then generate a basic SSEMENT with only this EP in the RELS list. Next, the `graph_to_mrs` function will recurse down to 'red' and follow the same process to get a basic SSEMENT with the adjective EP. Lastly, the function will call `edge_to_mrs`. This function will use the edge text (in this case `color`) to first search the lexicon for what kind of composition the property calls for, here this would be `adjective_ssement`. Then the function searches `comp_to_graph_relations.json` to figure out in what configuration the composition must occur. For this example, the result is `PARENT_PLUG` because the child, `red` is the semantic functor that plugs its `ARG1` with the `ARG0` of the parent node's MRS. The reason it is necessary to do this check is because when recursing the graph, the traversal will occur in the same "direction" every time, but the composition may require either the parent or child to serve as the functor, so it would not be viable to assume one over the other.  


## mrs_util.py
Various functions that are useful/necessary when performing MRS composition from scratch.

- `check_if_quantified(check_ssement)` -- check if the provided SSEMENT has been quantified already 
- `wrap_with_quantifier(unquant_ssement)` -- wrap the given SSEMENT in a quantifier
- `group_equalities(eqs)` -- given a list of EQs, group them into groups of equalities. For example, if the EQs list states that `x1=x2` and `x2=x3` an equality group should be created stating `x1=x2=x3` so it's clear all of those variables represent the same thing. 
- `get_most_specified_variable(eq_vars)` -- Given a set of variables that are all equal to each other, one of them must be chosen to "represent" the group in the final MRS. The one with the most specific type should be chosen. That is, if `i1=x2`, `x2` is more specific as `x` is a subtype of `i`.
- `overwrite_eqs(final_ssement)` -- Given a fully composed SSEMENT, all EQs must be overwritten with one "representative" for each set of equalities, this function performs that overwrite.
- `wrap_and_generate(final_ssement)` -- Mostly necessary specifically for referring expressions, a fully composed SSEMENT with EQs overwritten still must be wrapped with one final `unknown` predicate whose `ARG` is of type `e` because the ERG requires that an MRS have a top level INDEX of type `e` to generate, and a referring expression usually will havea top level INDEX of type `x` for the entity being described. So, this function adds the `unknown` predicate and then performs the generation. 


## Example Files
The following files contain examples of different portions of the pipeline for development, testing, and illustrative purposes. 

### composition_examples.py
Examples of composition being performed, agnostic to any graphs, just testing whether the MRS composition functions from `composition_library.py`, and by extension the algebra functions from `mrs_algebra.py`, work 