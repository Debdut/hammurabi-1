from akkadian import *


# RULES


def spouse_of(p):
    return ToScalar(_spouse_of(p))


# def is_married(p):
#     return _is_married(p)


def married(a, b):
    return Or(_family_relationship(a, b) == "Spouse",
              _family_relationship(b, a) == "Spouse",
              _spouse_of(a) == b,
              _spouse_of(b) == a)


def is_single(p):
    return Not(is_married(p))


# INPUTS

# What is {1}'s relationship with {0}?
# Options: ['Spouse', 'Parent', 'Child', 'Grandparent', 'Grandchild', 'Aunt/Uncle', 'Niece/Nephew', 'Cousin',
# 'Unrelated']
def _family_relationship(a, b):
    return In('str', 'fam.family_relationship', a, b, "What is {1}'s relationship with {0}?")


# Is {0} married?
def is_married(p):
    return In('bool', 'fam.is_married', p, None, "Is {0} married?")


# What is the name of {0}'s spouse?
# Should always ask _is_married(p) before asking this
def _spouse_of(p):
    return In('str', 'fam.spouse_of', p, None, "What is the name of {0}'s spouse?")
