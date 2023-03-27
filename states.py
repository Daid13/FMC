import random
from terms import (
    Term as Term,
    Variable as Variable,
    Abstraction as Abstraction,
    Application as Application,
    substitute as substitute,
)


class State:
    def __init__(self, term, memory=None) -> None:
        self.term = term
        if memory:
            self.memory = memory
        else:
            self.memory = {
                "in": Special_Stack(pop=lambda: Variable(int(input("integer input")))),
                "out": Special_Stack(
                    append=lambda o: print("output stream: " + str(o))
                ),
                "rnd": Special_Stack(
                    pop=random.randint(1, 100)
                ),  # arbitrary to pick 1-100 as range
                "": [],
            }

    def __str__(self) -> str:
        def print_stack(stack):
            stack_string = ""
            for t in stack:
                stack_string += str(t) + ", "
            return "[" + stack_string[:-2] + "]"

        def print_memory(memory):
            memory_string = ""
            for location in memory:
                if location not in ["in", "out", "rnd"]:
                    memory_string += (
                        location + ": " + print_stack(memory[location]) + ",\n"
                    )
            return "{" + memory_string[:-2] + "}"

        return str(self.term) + "\n" + print_memory(self.memory)

    def step(self):  # returns bool of success
        # print(type(self.term))
        if isinstance(self.term, Application):
            if self.term.location in self.memory:
                self.memory[self.term.location].append(self.term.argument)
            else:
                self.memory[self.term.location] = [self.term.argument]
            self.term = self.term.function
            return True
        elif isinstance(self.term, Abstraction):
            # print("hi")
            # print(self.term)
            if self.term.location in self.memory:
                temp = self.memory[self.term.location].pop()
            else:  # assumes an empty stack contains infinite Nones
                temp = None
            # print(temp,self.term.value)
            self.term = substitute(self.term.body, temp, self.term.value)
            # print(self.term)
            return True
        elif isinstance(
            self.term, Variable
        ):  # all variables including stack operations
            # Evaluating constants at this point is valid however it would be better to do it else where
            # print(self.term.value)
            if self.term.value == "+":  # addition, add print etc here?
                self.memory[""].append(
                    Variable(self.memory[""].pop().value + self.memory[""].pop().value)
                )
            elif self.term.value == "*":
                self.memory[""].append(
                    Variable(self.memory[""].pop().value * self.memory[""].pop().value)
                )
            elif self.term.value == "and":
                self.memory[""].append(
                    Variable(
                        self.memory[""].pop().value and self.memory[""].pop().value
                    )
                )
            elif (
                self.term.value == "if"
            ):  # warning, without type checking most things other than 0 will be true.
                if self.memory[""].pop():
                    t = self.memory[""].pop()
                    self.memory[""].pop()
                    self.memory[""].append(t)
                else:
                    self.memory[""].pop()
            # elif self.term.value=="while":
            # while N M ~>  [M . while N M] . [] . N . if
            #    M=self.memory[""].pop()
            #   N=self.memory[""].pop()

            elif "get" in self.term.value:
                l = self.term.value.split()
                # if l[0]=="get" way to check it actually is get in the right place.
                t = self.memory[l[1]].pop()
                self.memory[l[1]].append(t)
                self.memory[""].append(t)
            elif "set" in self.term.value:
                l = self.term.value.split()
                # if l[0]=="set" way to check it actually is get in the right place.
                self.memory[l[1]].pop()
                self.memory[l[1]].append(self.memory[""].pop())
            else:
                print("No step available: Variable ", self.term.value)
                return False
            self.term = self.term.next
            return True
        else:  # None case
            print("No step available: None")
            print(self)
            return False

    def run(self):
        step_result = True
        while step_result:
            step_result = self.step()
            # print(self)


class Special_Stack:
    def __init__(self, pop=None, append=None):
        self.append = append
        self.pop = pop
