import hammurabi.shared.fam as fam

from akkadian import *


# TAX YEAR


# Individual tax determinations are always on the last day of the calendar year
def assessment_date(p):
    return Date(tax_year(p), 12, 31)


# Tax year
def tax_year(p):
    return In("string", "us.fed.tax.indiv.shared.tax_year", p, None,
              "What tax year does {0} want to know about?")


# FILING STATUSES


# "Single" filing status
def filing_single(p):
    return And(Not(fam.is_married(p)),
               tax_status(p) == "Single")


# "Married filing jointly" filing status
def mfj(p):
    return And(fam.is_married(p),
               tax_status(p) == "Married filing jointly")


# "Married filing separately" filing status
def mfs(p):
    return And(fam.is_married(p),
               tax_status(p) == "Married filing separately")


# "Head of household" filing status
def hoh(p):
    return tax_status(p) == "Head of household"


# "Qualifying widow(er)" filing status
def qualifying_widower(p):
    return tax_status(p) == "Qualifying widow(er) with dependent child"


# Filing status input
def tax_status(p):
    return In("str", "us.fed.tax.indiv.shared.tax_status", p, None,
              question="What is {0}'s " + ToScalar(tax_year(p)) + " tax filing status?",
              options=["Single", "Married filing jointly", "Married filing separately", "Head of household",
                       "Qualifying widow(er) with dependent child"])


# DEDUCTIONS


# Itemizing deductions
def itemizing(p):
    return In("bool", "us.fed.tax.indiv.shared.itemizing", p, None,
              "Does {0} plan to itemize or claim adjustments to income in " + ToScalar(tax_year(p)) + "?")
