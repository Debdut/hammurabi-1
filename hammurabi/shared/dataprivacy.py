from akkadian import *
import hammurabi.shared.geo as geo


# DATA MODEL


activity_date = None
date_of_data_collection = None
subject_type = None
controller_type = None
processor_type = None
recipient_type = None
subject_country_region = None
recipient_country = None
controller_industry = None
processor_industry = None
source = ["Data subject", "Public register", "Public domain", "Third party"]
collection_purposes = None
subject_age = None
is_student = None
anonymization_type = None


# Country in which the data subject lives
def subject_country(data):
    return geo.country_of_residence(subject(data))


# Country in which the data controller is located
def controller_country(data):
    return geo.country_location(controller(data))


# Country in which the data processor is located
def processor_country(data):
    return geo.country_location(processor(data))


def industry_is(data):
    return "TODO"


# Is the intended activity the one specified?
def activity_is(data, activity):
    return IntersectionQ(intended_activities(data), [activity])


# Do the intended activities include any of the listed items?
def activity_is_any(data, activities: list):
    return IntersectionQ(intended_activities(data), activities)


# Is the content of the data the one specified?
def content_is(data, content):
    return IntersectionQ(contents(data), [content])


# Does the data contain any of the listed contents?
def content_is_any(data, content_list):
    return IntersectionQ(contents(data), content_list)


# Was the data processed for the specified reason?
def processing_purpose_is(data, purpose):
    return IntersectionQ(processing_purposes(data), [purpose])


# Was the data processed for one of the listed reasons?
def processing_purpose_is_any(data, purposes):
    return IntersectionQ(processing_purposes(data), purposes)


# HIGH-LEVEL RULE


# Determines whether a data-related activity complies with global laws on data privacy and protection
# This rule may have to go in another namespace (intl.trans?) to prevent circular references
def is_compliant(data):
    return False


# LISTS RELATED TO FACTS


list_of_activities = ["Collection", "Deletion", "Disclosure", "Processing", "Publication", "Transfer", "Storage"]

list_of_entity_types = ["Natural person", "Corporation", "Nonprofit organization", "National government",
                        "Subnational government", "Intergovernmental organization"]

list_of_industries = ["Public communications network", "Video rental or distribution"]

list_of_contents = ["Address", "Age", "Audio", "Authenticating information", "Biometric", "Civil legal judgment",
                    "Consumer credit information", "Criminal history", "Cultural data", "Customer purchase history",
                    "Date of birth", "Economic data", "Educational information", "Family information", "Financial data",
                    "Financial messaging data", "Gender", "Genetic", "Health data", "IP address", "Name",
                    "National identifier", "Occupation", "Online identifier", "Organizational title",
                    "Passenger name record", "Photograph", "Political opinion", "Racial or ethnic origin",
                    "Religious or other belief", "Sex life information", "Social data", "Telephone number", "Location",
                    "Trade union membership", "Unique identifier", "Vehicle data", "Video"]

list_of_purposes = ["Artistic or literary expression", "Authentication", "Religious membership", "Clinical trial",
                    "Compliance with legal obligation", "Consumer credit evaluation", "Contract performance",
                    "Criminal procedure", "Employment law or relations", "Exercise of official authority",
                    "Financial transaction", "Historical", "Insurance claim processing", "Journalism",
                    "Law enforcement", "Legal proceeding or claim", "Marketing", "National security",
                    "Necessary legitimate interests of controller", "Necessary legitimate interests of third party",
                    "Nonprofit membership processing", "Official statistics", "Payment processing",
                    "Payment collection", "Personal or household activity", "Profiling", "Provision of healthcare",
                    "Public health", "Public interest", "Public security", "Scientific", "Statistical", "Surveillance",
                    "Telecommunications", "Vital interests of the data subject", "Vital interests of third party"]

list_of_consent_types = ["Data subject consent", "Parental consent", "Data subject incapable of giving consent",
                         "Data made public by data subject"]

list_of_anonymization_types = ["Anonymized", "Pseudonymized", "Neither"]


# INPUTS


def subject(data):
    return In("str", "shared.dataprivacy.data_subject", data, None, "Who is the data subject?")


def controller(data):
    return In("str", "shared.dataprivacy.data_controller", data, None, "Who is the data controller?")


def processor(data):
    return In("str", "shared.dataprivacy.data_processor", data, None, "Who is the data processor?")

def contents(data):
    return In("list", "shared.dataprivacy.contents", data, None,
              question="What are the contents of the data?",
              options=list_of_contents)

def intended_activities(data):
    return In("list", "shared.dataprivacy.intended_activities", data, None,
              "What does the data controller intend to do with the data?")    # "data controller"?

def processing_purposes(data):
    return In("list", "shared.dataprivacy.processing_purposes", data, None,
              question="For what purpose(s) is the data being processed?",
              options=list_of_purposes)

def subject_consent(data):
    return In("bool", "shared.dataprivacy.subject_content", data, None,
              "Did the data subject consent to the proposed use(s) of their data?")
