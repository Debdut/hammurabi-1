from akkadian import *
import hammurabi.us.fed.tax.indiv.withholding as w4
import hammurabi.us.fed.tax.indiv.shared as tax


ApplyRules([(w4.form_w4_complete, 'Jim')])
