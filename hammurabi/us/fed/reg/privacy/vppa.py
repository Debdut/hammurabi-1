from akkadian import *
import hammurabi.shared.dataprivacy as dp
import hammurabi.us.shared.geo as geo


# Video Privacy Protection Act of 1988 (VPPA)
# 18 U.S.C. 2710


# Applicability


# Assuming a broad territorial scope
def vppa_applies(data):
    return And(EffectiveFrom('1988-11-05'),
               dp.industry_is("Video rental or distribution"),  # data?
               Or(geo.is_us_or_us_territory(dp.processor_country(data)),
                  geo.is_us_or_us_territory(dp.controller_country(data)),
                  geo.is_us_or_us_territory(dp.subject_country(data))))


# Sec. 2710(b)(1) - Non-disclosure requirement
def violates_vppa_b1(data):
    return And(dp.activities_include(data, ["Disclosure", "Publication", "Transfer"]),
               content_includes(data, ["Address", "Authenticating information", "Customer purchase history",
                                       "Date of birth", "Gender", "IP address", "Name", "Online identifier",
                                       "Telephone number", "Location", "Unique identifier"]),
               Not(disclosure_exception_applies(data)))


# Sec. 2710(b)(2) - Exceptions to non-disclosure requirement
def disclosure_exception_applies(data):
    return Or(subject_consent(data),    # (b)(2)(B)
              # (b)(2)(C), (b)(3)
              processing_purpose_includes(data, ["Criminal procedure", "Law enforcement", "Public security"]),
              # (b)(2)(D)
              And(content_is_any(data, ["Name", "Address"]),
                  Or(Not(content_is(data, "Customer purchase history")),
                     processing_for(data, "Marketing"))),
              # (b)(2)(F)
              processing_purpose_includes(data, ["Compliance with legal obligation", "Legal proceeding or claim"]))


# Sec. 2710(e) - Destruction of old records
def risk_of_violating_sec2710e(data):
    return activity_is("Storage")
