class Term:
    def __init__(self, location):
        self.location = location

    def compose():
        pass

    def free_values(self):
        pass

    def rename(self, old, new):
        pass

    def used_values(self):
        pass


class Variable(Term):
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

    def __str__(self) -> str:
        if self.next:
            return str(self.value) + "." + str(self.next)
        else:
            return str(self.value)

    def compose(self, M):
        if self.next:
            self.next.compose(M)
        else:
            self.next = M

    def free_values(self):
        return {self.value}

    def rename(self, old, new):
        if self.value == old:
            self.value = new

    def used_values(self):
        return {self.value}


# M is function, N is argument, N will be in []
class Application(Term):
    def __init__(self, location, function, argument):
        self.function = function
        self.argument = argument
        super().__init__(location)

    def __str__(self) -> str:
        return "[" + str(self.argument) + "]" + self.location + "." + str(self.function)

    def compose(self, M):
        # print("app comp", str(self))
        if self.function:  # deal with none parsed as variable
            print("composing with function", self, M)
            self.function.compose(M)
        else:
            print("replacing None", M)
            self.function = M
        # print(str(self))

    def free_values(self):
        return self.argument.free_values() | self.function.free_values()

    def rename(self, old, new):
        self.argument.rename(old, new)
        self.function.rename(old, new)

    def used_values(self):
        return self.argument.used_values() | self.function.used_values()


class Abstraction(Term):
    def __init__(self, location, value, body):
        self.value = value
        self.body = body
        super().__init__(location)

    def __str__(self) -> str:
        return self.location + "<" + self.value + ">." + str(self.body)

    def compose(self, M):  # this needs to also check something to do with freeness
        if M and self.value in M.free_values():
            self.rename(self.value, generate_fresh())
        if self.body:
            print("ab", self, M)
            self.body.compose(M)
        else:
            self.body = M

    def free_values(self):
        fv = self.body.free_values()
        fv.discard(self.value)
        return fv

    def rename(self, old, new):
        if self.value == old:
            self.value = new
        self.body.rename(old, new)

    def used_values(self):
        return self.body.used_values() | {self.value}
    
    def reduce(self):
        if isinstance(self.body,)



def substitute(term, new_term, old_value):  # returns rather than works in place
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
