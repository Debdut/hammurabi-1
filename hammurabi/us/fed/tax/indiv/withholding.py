import hammurabi.shared.fam as fam
import hammurabi.us.fed.tax.indiv.shared as tax

from akkadian import *


# https://www.irs.gov/pub/irs-pdf/fw4.pdf
# IRS Form W4 (2019) rules

# The following abbreviations are used in the rules below:
#
#   p = person
#   s = person's spouse
#   pa_wksht = Personal Allowances Worksheet
#   daai_wksht = Deductions, Adjustments, and Additional Income Worksheet
#   temj_wksht = Two-Earners/Multiple Jobs Worksheet
#   ctc = Child Tax Credit
#   mfj = Married filing jointly
#   mfs = Married filing separately
#   hoh = Head of household
#   dep = dependent


# Source rules

def form_w4_complete(p):
    return AsOf(tax.assessment_date(p), And(pa_wksht_complete(p),
                                            Or(Not(tax.itemizing(p)),
                                               daai_wksht_complete(p)),
                                            Or(Not(temj_wksht_required(p)),
                                               temj_wksht_complete(p))))


# PERSONAL ALLOWANCES WORKSHEET


# can we make person/spouse global?
def pa_wksht_complete(p):
    # check complete if line h is known?
    return pa_wksht_line_h(p) >= 0


# • You’re single, or married filing separately, and have only one job; or
# •  You’re married filing jointly, have only one job, and your spouse doesn’t work; or
# • Your wages from a second job or your spouse’s wages (or the total of both) are $1,500 or less
# dev question, could we infer "only one job" as one active wages/employment record? Probably a question for policy team.
def only_job_or_low_wage_second(p):
    return Or(And(Or(fam.is_single(p),
                     tax.mfs(p)),
                  has_only_one_job(p)),
              And(tax.mfj(p),
                  has_only_one_job(p),
                  unemployed(fam.spouse_of(p))),
              combined_couple_wages(p, fam.spouse_of(p)) <= 1500)


# Child tax credit. See Pub. 972, Child Tax Credit, for more information.
# • If your total income will be less than $71,201 ($103,351 if married filing jointly), enter 4 for each eligible child.
# • If your total income will be from $71,201 to $179,050 ($103,351 to $345,850 if married filing jointly), enter 2 for each
# eligible child.
# • If your total income will be from $179,051 to $200,000 ($345,851 to $400,000 if married filing jointly), enter 1 for
# each eligible child.
# • If your total income will be higher than $200,000 ($400,000 if married filing jointly), enter -0- . . . . . . .
def ctc_count(p):
    If(tax.mfj(p), ctc_w_spouse(p, fam.spouse_of(p)), ctc_w_o_spouse(p))


def ctc_w_spouse(p, s):
    return If(joint_income(p, s) < 103351, 4 * num_ctc_children(p),
              joint_income(p, s) <= 345850, 2 * num_ctc_children(p),
              joint_income(p, s) <= 400000, num_ctc_children(p),
              0)


def ctc_w_o_spouse(p):
    return If(total_income(p) < 71201, 4 * num_ctc_children(p),
              total_income(p) <= 179051, 2 * num_ctc_children(p),
              total_income(p) <= 200000, num_ctc_children(p),
              0)


# Credit for other dependents. See Pub. 972, Child Tax Credit, for more information.
# • If your total income will be less than $71,201 ($103,351 if married filing jointly), enter “1” for each eligible dependent.
# • If your total income will be from $71,201 to $179,050 ($103,351 to $345,850 if married filing jointly), enter “1” for every
# two dependents (for example, “-0-” for one dependent, “1” if you have two or three dependents, and “2” if you have
# four dependents).
# • If your total income will be higher than $179,050 ($345,850 if married filing jointly), enter “-0-” . . . . . .
def credit_for_other_deps(p):
    return If(tax.mfj(p), credit_for_other_deps_w_spouse(p, fam.spouse_of(p)),
              credit_for_other_deps_w_o_spouse(p))


def credit_for_other_deps_w_spouse(p, s):
    return If(joint_income(p, s) < 103351, num_ctc_dependents(p),
              joint_income(p, s) <= 345850, Floor(num_ctc_dependents(p) / 2),
              joint_income(p, s) > 345850, 0)


def credit_for_other_deps_w_o_spouse(p):
    return If(total_income(p) < 71201, num_ctc_dependents(p),
              total_income(p) <= 179051, Floor(num_ctc_dependents(p) / 2),
              total_income(p) > 179050, 0)


# Total on line h
def pa_wksht_line_h(p):
    return Boole(is_claiming_self(p)) \
           + Boole(tax.mfj(p)) \
           + Boole(tax.hoh(p)) \
           + Boole(only_job_or_low_wage_second(p)) \
           + Boole(ctc_count(p)) \
           + credit_for_other_deps(p) \
           + other_credits_pub505(p)


# Deductions, Adjustments, and Additional Income Worksheet


# Note: Use this worksheet only if you plan to itemize deductions, claim certain adjustments to income, or have a large
# amount of nonwage
# income not subject to withholding.
def daai_wksht_complete(p):
    return ded_adj_adtl_inc_line_10(p) >= 0


# Enter an estimate of your itemized deductions. These include qualifying home mortgage interest,
# charitable contributions, state and local taxes (up to $10,000), and medical expenses in excess of 10% of
# your income. See Pub. 505 for details . . . . . . . . . . . . . . . . . . . . . .
def ded_adj_adtl_inc_line_1(p):
    return itemized_deductions(p)


# 2 Enter: { $24,400 if you’re married filing jointly or qualifying widow(er)
# $18,350 if you’re head of household
# $12,200 if you’re single or married filing separately } . .
def ded_adj_adtl_inc_line_2(p):
    return If(Or(tax.mfj(p), tax.qualifying_widower(p)), 24400,
              tax.hoh(p), 18350,
              Or(fam.is_single(p), tax.mfs(p)), 12200)


# Subtract line 2 from line 1. If zero or less, enter “-0-”
def ded_adj_adtl_inc_line_3(p):
    return If(ded_adj_adtl_inc_line_1(p) - ded_adj_adtl_inc_line_2(p) >= 0,
              ded_adj_adtl_inc_line_1(p) - ded_adj_adtl_inc_line_2(p),
              False)


# Enter an estimate of your adjustments to income, qualified business income deduction, and any
# additional standard deduction for age or blindness (see Pub. 505 for information about these items) . .
def ded_adj_adtl_inc_line_4(p):
    return estimate_adj_to_inc_qual_bus_inc_ded_addtl_std_ded(p)


# Add lines 3 and 4 and enter the total
def ded_adj_adtl_inc_line_5(p):
    return ded_adj_adtl_inc_line_3(p) + ded_adj_adtl_inc_line_4(p)


# Enter an estimate of your nonwage income not subject to withholding (such as dividends or interest) .
def ded_adj_adtl_inc_line_6(p):
    return estimate_nonwage_inc_not_subj_to_withholding(p)


# Subtract line 6 from line 5. If zero, enter “-0-”. If less than zero, enter the amount in parentheses
def ded_adj_adtl_inc_line_7(p):
    return ded_adj_adtl_inc_line_5(p) - ded_adj_adtl_inc_line_6(p)


# Divide the amount on line 7 by $4,200 and enter the result here. If a negative amount, enter in parentheses.
# Drop any fraction
def ded_adj_adtl_inc_line_8(p):
    return Floor(ded_adj_adtl_inc_line_7(p) / 4200)


# Enter the number from the Personal Allowances Worksheet, line H, above
def ded_adj_adtl_inc_line_9(p):
    return pa_wksht_line_h(p)


# Add lines 8 and 9 and enter the total here. If zero or less, enter “- 0 -”. If you plan to use the Two-Earners/
# Multiple Jobs Worksheet, also enter this total on line 1 of that worksheet on page 4. Otherwise, stop here
# and enter this total on Form W-4, line 5, page 1
def ded_adj_adtl_inc_line_10(p):
    return Max([ded_adj_adtl_inc_line_8(p) + ded_adj_adtl_inc_line_9(p), 0])


# Two Earners/Multiple Jobs Worksheet (TEMJ)


# Note: Use this worksheet only if the instructions under line H from the Personal Allowances Worksheet direct you here.

# If you have more than one job at a time
# or are married filing jointly and you and your spouse both work,
# and the combined earnings from all jobs exceed $53,000 ($24,450 if married filing jointly), see the
# Two-Earners/Multiple Jobs Worksheet on page 4 to avoid having too little tax withheld.
def temj_wksht_required(p):
    return Or(temj_wksht_required_single(p),
              temj_wksht_required_couple(p, fam.spouse_of(p)))


# complete if line 9 is known
def temj_wksht_complete(p):
    return temj_wksht_line_9(p)


def temj_wksht_required_single(p):
    return And(count_of_jobs(p) > 1,
               total_income(p) > 53000)


def temj_wksht_required_couple(p, s):
    return And(tax.mfj(p),
               couple_both_work(p, s),
               combined_couple_wages(p, s) > 24450)


# Enter the number from the Personal Allowances Worksheet, line H, page 3 (or, if you used the
# Deductions, Adjustments, and Additional Income Worksheet on page 3, the number from line 10 of that
# worksheet)
# tbd, logic to figure out which wksht has been completed
def temj_wksht_line_1(p):
    return If(tax.itemizing(p), ded_adj_adtl_inc_line_10(p),
              pa_wksht_line_h(p))


# Find the number in Table 1 below that applies to the LOWEST paying job and enter it here. However, if you’re
# married filing jointly and wages from the highest paying job are $75,000 or less and the combined wages for
# you and your spouse are $107,000 or less, don’t enter more than “3”
# TODO: Check this. I think this logic got butchered during my refactoring (MP)
def temj_wksht_line_2(p):
              # Case 1
    return If(And(tax.mfj(p),
                  highest_earning_job_from_couple(p, fam.spouse_of(p)) <= 75000,
                  combined_couple_wages(p, fam.spouse_of(p))),
              # assumes only one job, needs to be expanded
              Min([3, temj_wksht_tbl_1_mfj(Min([annual_wages(p), annual_wages(fam.spouse_of(p))]))]),
              # Case 2
              tax.mfj(p), temj_wksht_tbl_1_mfj(combined_couple_wages(p, fam.spouse_of(p))),
              # Case 3
              temj_wksht_tbl_1_others(annual_wages(p)))


# If line 1 is more than or equal to line 2, subtract line 2 from line 1. Enter the result here (if zero, enter “-0-”)
# and on Form W-4, line 5, page 1. Do not use the rest of this worksheet
def temj_wksht_line_3(p):
    return If(temj_wksht_line_1(p) >= temj_wksht_line_2(p),
              temj_wksht_line_2(p) - temj_wksht_line_1(p),
              temj_wksht_line_4(p))


# Note: If line 1 is less than line 2, enter “-0-” on Form W-4, line 5, page 1. Complete lines 4 through 9 below to
# figure the additional withholding amount necessary to avoid a year-end tax bill.
# Enter the number from line 2 of this worksheet
def temj_wksht_line_4(p):
    return temj_wksht_line_2(p)


# Enter the number from line 1 of this worksheet
def temj_wksht_line_5(p):
    return temj_wksht_line_1(p)


# Subtract line 5 from line 4
def temj_wksht_line_6(p):
    return temj_wksht_line_4(p) - temj_wksht_line_5(p)


# Find the amount in Table 2 below that applies to the HIGHEST paying job and enter it here
def temj_wksht_line_7(p):
    return If(tax.mfj(p),
              # assumes one job, needs to be expanded
              temj_wksht_tbl_2_mfj(Max([annual_wages(p), annual_wages(fam.spouse_of(p))])),
              temj_wksht_tbl_2_others(annual_wages(p)))


# Multiply line 7 by line 6 and enter the result here. This is the additional annual withholding needed
def temj_wksht_line_8(p):
    return temj_wksht_line_6(p) * temj_wksht_line_7(p)


# Divide line 8 by the number of pay periods remaining in the year. For example, divide by 18 if you’re paid every
# 2 weeks and you complete this form on a date in late April when there are 18 pay periods remaining in
# the year. Enter the result here and on Form W-4, line 6, page 1. This is the additional amount to be withheld
# from each paycheck
def temj_wksht_line_9(p):
    return Trunc(temj_wksht_line_8(p) / pay_periods_remaining_in_year(p))


def highest_earning_job_from_couple(p, s):
    return Max([highest_earning_job_wages(p), highest_earning_job_wages(s)])


def temj_wksht_tbl_2_mfj(wages):
    return If(wages <= 24900, 420,
              wages <= 84450, 500,
              wages <= 173900, 910,
              wages <= 326950, 1000,
              wages <= 413700, 1330,
              wages <= 617851, 1450,
              1540)


def temj_wksht_tbl_2_others(wages):
    return If(wages <= 7200, 420,
              wages <= 36975, 500,
              wages <= 81700, 910,
              wages <= 158225, 1000,
              wages <= 201600, 1330,
              wages <= 507800, 1450,
              1540)


def temj_wksht_tbl_1_mfj(wages):
    return If(wages <= 5000, 0,
              wages <= 9500, 1,
              wages <= 19500, 2,
              wages <= 35000, 3,
              wages <= 40000, 4,
              wages <= 46000, 5,
              wages <= 55000, 6,
              wages <= 60000, 7,
              wages <= 70000, 8,
              wages <= 75000, 9,
              wages <= 85000, 10,
              wages <= 95000, 11,
              wages <= 125000, 12,
              wages <= 155000, 13,
              wages <= 165000, 14,
              wages <= 175000, 15,
              wages <= 180000, 16,
              wages <= 195000, 17,
              wages <= 205000, 18,
              19)


def temj_wksht_tbl_1_others(wages):
    return If(wages <= 7000, 0,
              wages <= 13000, 1,
              wages <= 27500, 2,
              wages <= 32000, 3,
              wages <= 40000, 4,
              wages <= 60000, 5,
              wages <= 75000, 6,
              wages <= 85000, 7,
              wages <= 95000, 8,
              wages <= 100000, 9,
              wages <= 110000, 10,
              wages <= 115000, 11,
              wages <= 125000, 12,
              wages <= 135000, 13,
              wages <= 145000, 14,
              wages <= 160000, 15,
              wages <= 180000, 16,
              17)


# HOUSEHOLD EMPLOYMENT AND INCOME


def unemployed(s):
    return employment_status(s) != "Employed"


# Total income of a person and their spouse
def joint_income(p, s):
    return total_income(p) + total_income(s)


# TODO: Is this correct policywise?
# wages from person's first job, wages from spouse's job
def combined_couple_wages(p, s):
    return wages_from_second_job(p) + annual_wages(s)


def has_only_one_job(p):
    return count_of_jobs(p) == 1



# For brevity; only available in this module
def _year(p):
    return ToScalar(tax.tax_year(p))


# INPUTS


def is_claiming_self(p):
    return In("bool", "claim_self", p, None,
              question="Does {0} intend to claim a deduction for him/herself in " + _year(p) + "?")


def employment_status(p):
    return In("str", "employment_status", p, None, "What is {0}'s employment status?",
              options=["Employed", "Not employed"])


def wages_from_second_job(p):
    return In("num", "second_job_wages", p, None,
              "What was {0}'s total wages from his/her second job in " + _year(p) + "?")


def annual_wages(p):
    return In("num", "wages", p, None, "What was {0}'s total wages in " + _year(p) + "?")


def count_of_jobs(p):
    return In("num", "number_of_jobs", p, None, "How many jobs did {0} simultaneously hold in " + _year(p) + "?")


def other_credits_pub505(p):
    return In("num", "other_credits_pub505", p, None,
              question="How many other credits does {0} have from Worksheet 1-6 of Pub. 505?",
              help="Enter 0 if none.")


# temporal?
def itemized_deductions(p):
    return In("num", "itemized_deductions", p, None,
              question="Please enter an estimate of {0}'s itemized deductions for " + _year(p) + ".",
              help="These include qualifying home mortgage interest, "
              + "charitable contributions, state and local taxes (up to $10,000), and medical expenses in excess of "
              + "10% of your income. See Pub. 505 for details")


def estimate_adj_to_inc_qual_bus_inc_ded_addtl_std_ded(p):
    return In("num", "estimate_adj_to_inc_qual_bus_inc_ded_addtl_std_ded", p, None,
              question="Enter an estimate of {0}'s adjustments to income, "
              + "qualified business income deduction, and any additional standard deduction for age or blindness"
                "for " + _year(p) + ".",
              help="See Pub. 505 for more information about these items.")


def estimate_nonwage_inc_not_subj_to_withholding(p):
    return In("num", "estimate_nonwage_inc_not_subj_to_withholding", p, None,
              question="Enter an estimate of {0}'s nonwage income not subject to withholding for " + _year(p) + ".",
              help="Dividends and interest are examples of such income.")


def highest_earning_job_wages(p):
    return In("num", "highest_earning_job_total_wages", p, None,
              question="How much did {0} make in wages from his/her highest earning job in " + _year(p) + ".")


# TODO: Ask about each person separately
def couple_both_work(p, s):
    return In("bool", "couple_both_work", p, s, "Do {0} and {1} both work?")


# TODO: This should be calculated from some lower-level facts
def pay_periods_remaining_in_year(p):
    return In("num", "pay_periods_remaining", p, None,
              question="Enter the number of pay periods remaining in the year for {0}.",
              help="For example, divide by 18 if you’re paid every 2 weeks and it is a date " +
              "in late April when there are 18 pay periods remaining in the year")


def total_income(p):
    return In("num", "total_income", p, None, "What is {0}'s total annual income?")


def num_ctc_children(p):
    return In("num", "number_children_pub_972", p, None,
              "Enter the number of eligible children from Publication 972, Child Tax Credit for {0}.")


def num_ctc_dependents(p):
    return In("num", "num_dep_pub_972", p, None,
              "Enter the number of eligible dependents from Publication 972, Child Tax Credit for {0}.")
