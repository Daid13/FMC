import re

from terms import (
    Term as Term,
    Variable as Variable,
    Abstraction as Abstraction,
    Application as Application,
)
from states import State as State

POSSIBLEVALUES = set([chr(c) for c in range(65, 91)])
BINARYFUNCTIONS = ["+", "*", "and", "or", "while"]
TRINARYFUNCTIONS = ["if"]
FUNCTIONS = BINARYFUNCTIONS + TRINARYFUNCTIONS


def generate_fresh():
    t = current_state.term
    used = t.used_values()
    valid = POSSIBLEVALUES - used
    return next(iter(valid))


def run_inter_parse():
    print(inter_parse("a:=2;(<x>.!a)(a:=3;0)"))
    print(inter_parse("a:=2;([u].w).<y>.y"))
    print(inter_parse("(x=N);M"))


def run_demo():
    demo = "in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out"
    print("First we'll parse this string and use it as starting term:")
    print(demo)
    start_term = base_parse(demo)
    current_state = State(start_term)
    print("Which makes this the starting state, empty stacks and that term")
    print(current_state)
    print("Now doing a single step")
    current_state.step()
    print(current_state)
    print("Running till termination")
    current_state.run()
    print(current_state)


def run_second_demo():
    demo = "((read;read);+);print"
    print("This time doing the same using keywords instead")
    start_term = inter_parse(demo)
    print(start_term)
    current_state = State(start_term)
    print("hi")
    current_state.run()
    print("hi")
    print(current_state)

    pass


# t1=base_parse("in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out")
# current_state=State(t1)
# current_state.run()
# test=Special_Stack(pop=lambda : int(input("integer input")))
# print(test.pop())
# run_demo()
# run_second_demo()
# current_state = State(None)
"""
l2=Variable("a", "x")
l1=Variable("a", "y", l2)
a1=Abstraction("a", "x", l1)
a2=Application("a",a1,l1)
a3=Application("a",l2,l2)
t1=
print(l1)
print(a1)
print(a2)
print(a3)
print(l2)
l2=substitute(l2,a3,"x")
print(l2)
print("run")
print(a2)
current_state=State(a2)
#s.run()
current_state.step()
print(current_state)
current_state.run()
print(current_state)
#s.test()"""
