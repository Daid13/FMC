# app.py
import states
import terms
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route("/")
def start():
    return render_template("input.html")
           
@app.route("/input/", methods = ["GET"])
def input():
    inp = request.args.get("input")#possibly add extra step of going via dict to get actual start term
    return redirect(url_for("home", term=inp))
    

@app.route("/home/<term>")
def home(term):
    inp_term={"addition":  "in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out",
              "stack": "[1].[2].<x>.<y>.x.x.+.y.+"}
    current_state=states.State(terms.base_parse(inp_term[term]))
    

    context={"current_state": current_state,
         "operation_result":""}
    return render_template("start.html",**context)

if __name__ == "__main__":
    app.run(debug=True)