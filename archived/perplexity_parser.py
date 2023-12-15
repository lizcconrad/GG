# ARCHIVED: 08/28/2023
# Now that I'm directly running the SWI-Prolog queries in python,
# there's no reason to parse text files with prolog output

import pyparsing as pp
import re
import sys


# pieces of the grammar

# Prolog wrapper, that is Var = [...]
# prologWrapper = ""


# property value
# any string without commas, brackets, or parentheses
# OR anything enclosed in {p} tags
property_value = pp.Regex("[^,()\[\]]*").set_results_name("property_value")

# name of the property
property_name = pp.Word(pp.alphanums + "_").set_results_name("property_name")

# property
entity_property = pp.Group(pp.Suppress("(") + property_name + pp.Suppress(",") + property_value + pp.Suppress(")")).set_results_name("entity_property")

# property list
property_list = pp.Group(pp.Suppress("[") + (pp.DelimitedList(entity_property) | "") + pp.Suppress("]")).set_results_name("property_list")

# name of the entity
entity_name = pp.Word(pp.alphanums + "_").set_results_name("entity_name")

# one individual entity
entity = pp.Group(pp.Suppress("(") + entity_name + pp.Suppress(",") + property_list + pp.Suppress(")")).set_results_name("entity")

# the full string should be a list of entities
entity_list = (pp.Suppress("[") + pp.DelimitedList(entity, ",") + pp.Suppress("]")).set_results_name("entity_list")


def parse_data_file(filename):
    """
    Take in a text file containing entities, properties of entities, and relationships of entities and parse it
    :param filename: text file containing entity data
    :type filename: str
    :return: results of the parse
    :rtype: ParseResults
    """
    with open(filename) as input_file:
        example_text = input_file.read()

    return entity_list.parse_string(example_text)

