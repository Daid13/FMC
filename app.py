# app.py
import states
import terms
from flask import (
    Flask,
    make_response,
    session,
    redirect,
    render_template,
    request,
    url_for,
)
import copy
import json
import jsonpickle

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def get_context():
    pass


@app.route("/")
def start():
    return render_template("input.html")


@app.route("/input/", methods=["GET"])
def input():
    if request.args.get("input"):
        inp = request.args.get(
            "input"
        )  # possibly add extra step of going via dict to get actual start term
        return redirect(url_for("home", inp=inp))
    else:
        inp=request.args.get("term_input")
        print(inp)
        inp=terms.base_parse(inp)
        print(inp)


@app.route("/home/<inp>/", methods=["GET", "POST"])
def home(inp):
    if request.method == "POST":
        print(2)
        if (
            request.form["next"] == "step"
        ):  # should display new term in operation result
            context = jsonpickle.decode(request.cookies.get("context"))
            temp = copy.deepcopy(context["current_state"])
            temp.step()
            context["operation_result"] = str(temp.term)
            resp = make_response(render_template("start.html", **context))
            resp.set_cookie("context", jsonpickle.encode(context))
            resp.set_cookie("action", "step")
        elif request.form["next"] == "confirm":
            if request.cookies.get("action") == "step":
                context = jsonpickle.decode(request.cookies.get("context"))
                context["current_state"].step()
                context["operation_result"] = ""
                resp = make_response(render_template("start.html", **context))
                resp.set_cookie("context", jsonpickle.encode(context))
                resp.set_cookie("action", "")
            elif request.cookies.get("action") == "":
                resp = make_response(render_template("start.html", **context))
                pass  # currently no action but maybe error message
    else:
        inp_term = {
            "addition": "in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out",
            "stack": "[1].[2].<x>.<y>.x.x.+.y.+",
            "multiplestacks": "[1]a.[2]b.[3]c.[4].[5].[6]b.[7]a.+",
        }
        print("in create")
        current_state = states.State(terms.base_parse(inp_term[inp]))
        context = {"current_state": current_state, "operation_result": "", "inp": inp}
        resp = make_response(render_template("start.html", **context))
        resp.set_cookie("context", jsonpickle.encode(context))
        resp.set_cookie("action", "")

    print(1)

    return resp


if __name__ == "__main__":
    app.run(debug=True)
