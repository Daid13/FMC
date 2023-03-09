import re
from terms import (
    Term as Term,
    Variable as Variable,
    Abstraction as Abstraction,
    Application as Application,
)
from states import State as State

POSSIBLEVALUES = set([chr(c) for c in range(65, 91)])
BINARYSTACK_CONSTANTS = ["+", "*", "and", "or", "while"]
TRINARYSTACK_CONSTANTS = ["if"]


def base_parse(s):
    l = s.split(".")
    # print(l)
    temp = bpr(l)
    # print(temp)
    return temp


def bpr(l):
    if l:
        t = l.pop(0)
        if "<" in t:
            temp = t.split("<")
            location = temp[0]
            value = temp[1][:-1]  # getting rid of >
            return Abstraction(location, value, bpr(l))
        elif "[" in t:
            list1 = [t[1:]]
            while "]" not in list1[-1]:  # this doesn'thandle nesting correctly
                list1.append(l.pop(0))

            temp = list1.pop().split("]")
            list1.append(temp[0])
            location = temp[1]
            return Application(location, bpr(l), bpr(list1))
        elif t != "None":
            return Variable(t, bpr(l))
    else:
        return None


IO_CONSTANTS = {
    "print": base_parse("<x>.[x]out"),
    "read": base_parse("in<x>.[x]"),
    "rand": base_parse("rnd<x>.[x]"),
}
# "if":,
# "while":,}


def generate_fresh():
    t = current_state.term
    used = t.used_values()
    valid = POSSIBLEVALUES - used
    return next(iter(valid))


def inter_parse(s):
    # desired data structure:
    stack = []

    for c in s:
        if c == ")":
            temp_list = []
            while stack[-1] != "(":
                temp_list.append(stack.pop())
            stack.pop()
            temp_list.reverse()
            stack.append(temp_list)
        else:
            stack.append(c)
    return ipr(stack)


def ipr(l):
    # print(l)
    s = ""
    for a in l:
        if isinstance(a, list):
            s += ipr(a)
        else:
            s += a

    def unpack_IO_constants(term):
        if isinstance(term, Variable):
            if term.value in IO_CONSTANTS:
                new = IO_CONSTANTS[term.value]
            return new.compose(unpack_IO_constants(term.next))
        elif isinstance(term, Application):
            return Application(
                term.location,
                unpack_IO_constants(term.function),
                unpack_IO_constants(term.argument),
            )
        elif isinstance(term, Abstraction):
            return Abstraction(
                term.location, term.value, unpack_IO_constants(term.body)
            )

    # do operationshere
    def do_operations(s):  # str to str
        if ";" in s:
            l = s.split(";")
            # print(l)
            t = base_parse(do_operations(l[0]))
            t.compose(base_parse(do_operations(l[1])))
            return str(t)
        elif ":" in s:
            l = s.split(":=")
            location = l[0]
            value = l[1]
            # print(l)
            return str(
                Abstraction(
                    location, "_", Application(location, None, base_parse(value))
                )
            )

        elif "=" in s:  # some other expressions include = so this must be done after
            l = s.split("=")
            return "[" + do_operations(l[1]) + "].<" + l[0] + ">"

        return str(base_parse(s))  # should be able to remove both layers

    # Types of operations
    # Binary: composition
    # Single replace: huh?
    # compose: term ; term
    # update: location := term
    # lookup: ! location

    # set: set location
    # get: get location
    # rand:
    # read:
    # print
    return do_operations(s)


# print(inter_parse("a:=2;(<x>.!a)(a:=3;0)"))
# print(inter_parse("a:=2;([u].w).<y>.y"))
# print(inter_parse("(x=N);M"))


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
    start_term = base_parse(inter_parse(demo))
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
run_demo()
run_second_demo()
current_state = State(None)
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
