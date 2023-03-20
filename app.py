# app.py
import states
import terms
from flask import Flask, session, redirect, render_template, request, url_for
import copy

app = Flask(__name__)
app.secret_key=b'_5#y2L"F4Q8z\n\xec]/'

def get_context():
    pass

@app.route("/")
def start():
    return render_template("input.html")
           
@app.route("/input/", methods = ["GET"])
def input():
    inp = request.args.get("input")#possibly add extra step of going via dict to get actual start term
    return redirect(url_for("home", inp=inp)) 

@app.route("/home/<inp>/", methods = ["GET", "POST"])
def home(inp):
    if request.method == "POST":
        print(2)
        if request.form["next"] == "step":#should display new term in operation result
            print(session.get("context"))
            temp=copy.deepcopy(session.context["current_state"])
            temp.step()
            session.context["operation_result"]=str(temp.term)
            session.action="step"
            return render_template("start.html",**session.context)
        elif request.form["next"] == "confirm":
            if session.action=="step":
                session.context["current_state"].step()
                session.context["operation_result"]=""
                session.action=""
            elif session.action=="":
                pass#currently no action but maybe error message
            return render_template("start.html",**session.context)
    else:
        inp_term={"addition":  "in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out",
              "stack": "[1].[2].<x>.<y>.x.x.+.y.+"}
        print("in create")
        session.context={"current_state": states.State(terms.base_parse(inp_term[inp])),
            "operation_result":"",
            "inp": inp}
        session.action=""
        session.modified=True
        session.permanent=True
        print(session.action)
        print(session.context)
        
    print(1)

    return render_template("start.html",**session.context)

if __name__ == "__main__":
    app.run(debug=True)