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
            self.function.compose(M)
        else:
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
        if self.value in M.free_values():
            self.rename(self.value, generate_fresh())
        if self.body:
            self.body.compose(M)
        else:
            self.body = M

    def free_values(self):
        return self.body.free_values().discard(self.value)

    def rename(self, old, new):
        if self.value == old:
            self.value = new
        self.body.rename(old, new)

    def used_values(self):
        return self.body.used_values() | {self.value}
