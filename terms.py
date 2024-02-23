from typing import Optional

class Term:
    def __init__(self, location:str) -> None:
        self.location = location

    def copy(self) -> 'Term':
        return base_parse(str(self))

    def compose(self, M: 'Term') -> None:
        pass

    def free_values(self) -> set:
        pass

    def rename(self, old: str, new: str) -> None:
        pass

    def used_values(self) -> set:
        pass


class Variable(Term):
    def __init__(self, value: str, next: Optional[Term] = None) -> None:
        self.value = value
        self.next = next

    def __str__(self) -> str:
        if self.next:
            return str(self.value) + "." + str(self.next)
        else:
            return str(self.value)

    def compose(self, M: Term) -> None:
        if self.next:
            self.next.compose(M)
        else:
            self.next = M

    def free_values(self) -> set:
        return {self.value}

    def rename(self, old: str, new: str) -> None:
        if self.value == old:
            self.value = new

    def used_values(self) -> set:
        return {self.value}


# M is function, N is argument, N will be in []
class Application(Term):
    def __init__(self, location: str, function: Term, argument: Term) -> None:
        self.function = function
        self.argument = argument
        super().__init__(location)

    def __str__(self) -> str:
        return "[" + str(self.argument) + "]" + self.location + "." + str(self.function)

    def compose(self, M: Term) -> None:
        if self.function:  # deal with none parsed as variable
            print("composing with function", self, M)
            self.function.compose(M)
        else:
            print("replacing None", M)
            self.function = M

    def free_values(self) -> set:
        return self.argument.free_values() | self.function.free_values()

    def rename(self, old: str, new: str) -> None:
        self.argument.rename(old, new)
        self.function.rename(old, new)

    def used_values(self) -> set:
        return self.argument.used_values() | self.function.used_values()


class Abstraction(Term):
    def __init__(self, location:str, value:str, body:Term) -> None:
        self.value = value
        self.body = body
        super().__init__(location)

    def __str__(self) -> str:
        return self.location + "<" + self.value + ">." + str(self.body)

    def compose(self, M:Term) -> None:  # this needs to also check something to do with freeness
        if M and self.value in M.free_values():
            self.rename(self.value, generate_fresh())
        if self.body:
            print("ab", self, M)
            self.body.compose(M)
        else:
            self.body = M

    def free_values(self) -> None:
        fv = self.body.free_values()
        fv.discard(self.value)
        return fv

    def rename(self, old:str, new:str):
        if self.value == old:
            self.value = new
        self.body.rename(old, new)

    def used_values(self) -> None:
        return self.body.used_values() | {self.value}


def substitute(term, new_term: Term, old_value: str) -> Term:  # returns rather than works in place
    new_term = base_parse(str(new_term))
    # print("sub")
    if isinstance(term, Variable):
        # print("into variable")
        if term.value == old_value:
            # print("values are the same")
            new_term.compose(substitute(term.next, new_term, old_value))
            return new_term
        else:
            term.next = substitute(term.next, new_term, old_value)
            return term
    elif isinstance(term, Application):
        term.function = substitute(term.function, new_term, old_value)
        term.argument = substitute(term.argument, new_term, old_value)
        return term
    elif isinstance(term, Abstraction):
        if term.value == old_value:
            return term
        else:
            if new_term == None or term.value not in new_term.free_values():
                term.body = substitute(term.body, new_term, old_value)
                return term
            else:
                term.rename(term.value, generate_fresh())

                return None
    else:
        # print("got to else")
        return None


def base_parse(s: str) -> Term:  # str->term
    l = s.split(".")
    # print(l)
    temp = bpr(l)
    # print(temp)
    return temp


def bpr(l: list) -> Term:  # list->term
    if l:
        t = l.pop(0)
        if "<" in t:
            temp = t.split("<")
            location = temp[0]
            value = temp[1][:-1]  # getting rid of >
            return Abstraction(location, value, bpr(l))
        elif "[" in t:
            list1 = [t[1:]]
            while "]" not in list1[-1]:  # this doesn't handle nesting correctly
                list1.append(l.pop(0))

            temp = list1.pop().split("]")
            list1.append(temp[0])
            location = temp[1]
            return Application(location, bpr(l), bpr(list1))
        elif t != "None":
            return Variable(t, bpr(l))
    else:
        return None


def inter_parse(s: str) -> Term:  # str->term
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
    return unpack_constants(ipr(stack))


CONSTANTS = {
    "print": "<x>.[x]out",
    "read": "in<x>.[x]",
    "rand": "rnd<x>.[x]",
}


def unpack_constants(t: Term) -> Term:  # term to term
    if isinstance(t, Variable):
        if t.value in CONSTANTS:
            temp = base_parse(CONSTANTS[t.value])
            print("unp", temp, t.next)

            temp.compose(unpack_constants(t.next))
            print(t.value, CONSTANTS[t.value])
            print("post", temp)
            return temp
        else:
            t.next = unpack_constants(t.next)
            return t
    elif isinstance(t, Application):
        return Application(
            t.location, unpack_constants(t.function), unpack_constants(t.argument)
        )
    elif isinstance(t, Abstraction):
        return Abstraction(t.location, t.value, unpack_constants(t.body))
    return None


def ipr(l: list) -> Term:  # list->term
    def do_operations(s: str) -> Term:  # str to term
        if ";" in s:
            l = s.split(";")
            # print(l)
            t = do_operations(l[0])
            t.compose(do_operations(l[1]))
            return t
        elif ":" in s:
            l = s.split(":=")
            location = l[0]
            value = l[1]
            # print(l)
            return Abstraction(
                location, "_", Application(location, None, base_parse(value))
            )
        elif "=" in s:  # some other expressions include = so this must be done after
            l = s.split("=")
            return base_parse(
                "[" + str(do_operations(l[1])) + "].<" + l[0] + ">"
            )  # refactor

        return base_parse(s)  # should be able to remove both layers

    # print(l)
    s = ""
    for a in l:
        if isinstance(a, list):
            s += str(
                ipr(a)
            )  # don't like this type change but can just be stripped out of this function
        else:
            s += str(a)

    return do_operations(s)
