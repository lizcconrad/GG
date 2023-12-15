# versions of the classes that don't inherit from the PyDelphin MRS/EP superclasses (archived 10/04/2023)
# MY RAW ASS VERSION . . . .
class Raw_SEP:
    """
    Wrapper class for the PyDelphin EP object
    An EP is a tuple of the form ...
    An SEP is a tuple of the form ...

    The key difference is the list of holes
    """
    def __init__(self, erg_predicate, var_lblr):
        # get synopsis of erg_predicate
        syn = smi.find_synopsis(erg_predicate)
        # calling this pre_args just because I want the actual args to point to the args in the EP object...
        # probably unnecessary but doing that for now
        args = concretize(var_lblr, syn)

        # create an EP object
        self.internal_ep = mrs.EP(erg_predicate, var_lblr.get_var_name('h'), args)
        self.holes = self.get_holes(args)

        # pointers into variables of the EP object, only doing the bare minimum now, can add more
        self.predicate = self.internal_ep.predicate
        self.label = self.internal_ep.label
        self.id = self.internal_ep.id
        self.args = self.internal_ep.args

    def get_holes(self, args):
        """
        Get the holes for an SEP
        :param args: List of arguments in the SEP
        :type args: dict
        :return: sep_holes, dict of holes
        :rtype: dict
        """
        # if it's not a quantifier, anything that isn't ARG0 is a hole
        # otherwise, ... ? they're all holes?
        sep_holes = {}

        # quantifier check, is RESTR in the list?
        if 'RESTR' in args:
            # if so, everything is a hole (possibly not BODY though...?)
            for arg in args:
                sep_holes[arg] = args[arg]
        else:
            # otherwise, anything that ISN'T ARG0 is a hole
            for arg in args:
                if arg != 'ARG0':
                    sep_holes[arg] = args[arg]

        print("SEP_HOLES: {}".format(sep_holes))
        return sep_holes

# MY RAW ASS VERSION . . .
class Raw_SSEMENT:
    """
    Wrapper class for the PyDelphin MRS object.
    An MRS is a tuple of the form <Hook, R, C> where...
        ... Hook is a tuple of the form <GT, Ind, Xarg> where ...
            ... GT is the top handle
            ... Index is the index
            ... Xarg is ... ? used to deal with raising/control constructions lol
        ... R is a bag of EPs, where an EP is a tuple of the form <handle, relation, (arg1, arg2,...), (sc-arg1, sc-arg2,...)>
            ... sometimes written as h1:every(x, h1, h2)
        ... C is a bag of handle constraints

    However, a SSEMENT has additional information, namely the holes. It is a tuple of the form <Hook, Holes, Lzt, Eqs> where ...
        ... Hook is a tuple of the form <GT, Ind, Xarg> where ...
            ... GT is the top handle
            ... Index is the index
            ... Xarg is ... ? used to deal with raising/control constructions lol
        ... Holes is the list of holes
        ... Lzt is the list of SEPs (analogous to R in an MRS)
        ... Eqs is a list of equalities between variables
        ... there are handle constraints, but I'm not positive how the paper represents them??
    Basically, the only thing SSEMENT has that MRS does not is Holes, so I'm creating an object that uses
    the PyDelphin MRS object and points to pieces of it, but also has Holes
    """
    def __init__(self, sep, var_lblr):
        # create an MRS object
        # have to use the internal_ep attribute of the SEP because PyDelphin is looking for a PyDelphin EP object,
        # not an SEP
        self.internal_mrs = mrs.MRS(var_lblr.get_var_name('h'), var_lblr.get_var_name('e'), [sep.internal_ep])

        # pointers into variables of the MRS object, only doing the bare minimum now, can add more
        self.top = self.internal_mrs.top
        self.index = self.internal_mrs.index
        self.predications = self.internal_mrs.predications
        self.rels = self.internal_mrs.rels
        self.variables = self.internal_mrs.variables
        self.hcons = self.internal_mrs.hcons

        # holes from the SEP :^)
        self.holes = sep.holes