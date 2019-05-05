from flask import session as web_session
from akkadian import *
from flask import Flask, render_template, request, jsonify
from hammurabi.us.fed.tax.indiv import withholding as withholding



goal = [(withholding.form_w4_complete, "Hub")]
#testing
# goal = [(withholding.combined_couple_wages, "hub", "sps")]


def investigate_goal():
    web_session['factSet'] = []
    return web_apply_rules(goal)
   


def call_on_form_post():
    #get answer from user/form
    answer = request.form['answer']

    #add user input and attribute to session
    fs = web_session['factSet']
    
    attr = web_session['queued_attr']
    
    #fs is now a list of dicts with each dict representing a fact object that will be converted
    fs.append(Fact(attr[1], attr[2], attr[3], convert_input(attr[0], answer)).__dict__)

    #clear previous session object to accept new list
    web_session.pop('factSet', None)
    
    #store facts as dict in factSet sesion variable (list)
    web_session['factSet'] = fs
    print('web session = ')
    print(web_session['factSet'])

    #convert to dict back to facts to call apply_rules
    convertedFactSet = dict_to_facts(web_session['factSet'])

    print("converted fact set")
    print(convertedFactSet)
    return web_apply_rules(goal, convertedFactSet)


def web_apply_rules(goals: list, fs=[]):
    #for debugging
    # return jsonify(ApplyRules(goals, fs))
    
    # Call the "apply rules" interface
    results = ApplyRules(goals, fs)

    # If all of the goals have been determined, present the results
    if results["complete"]:
        return results["msg"]  # TODO

    # print("Fact Set in web_apply_rules:")
    # for f in fs:
    #     print(f)

    # Otherwise, ask the next question...
    else:
        # Find out what the next question is
        nxt = results["missing_info"][0]

        # Ask it
        return collect_input(nxt)


def collect_input(attr):
    #store attribute in session so we know which question was being answered by the user
    web_session.pop("queued_attr", None)
    web_session["queued_attr"] = attr

    type = attr[0]
    public_name = attr[1]
    subject = attr[2]
    obj = attr[3]
    question = attr[4]
    options = attr[5]

    print(options)

    if(attr[5] is None):
        hint = ""
    else:
        hint = attr[5]

    return render_template('main_interview.html', type=type, question=question, hint=hint, options=options)
    #for debugging
    return jsonify(attr)


def dict_to_facts(sessionObject):
    fs = []
    print("session object = ")
    print(sessionObject)
    for f in sessionObject:
        print("converting this")
        print(f)
        fs.append(Fact(f['name'], f['subject'], f['object'], f['value']))
    return fs

