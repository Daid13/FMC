import re
import random

POSSIBLEVALUES=set([chr(c) for c in range(65,91)])
BINARYFUNCTIONS=["+","*", "and", "or", "while"]
TRINARYFUNCTIONS=["if"]
FUNCTIONS=BINARYFUNCTIONS+TRINARYFUNCTIONS


class Term:
    def __init__(self, location):
        self.location=location
    def compose():
        pass
    def free_values(self):
        pass
    def rename(self,old, new):
        pass
    def used_values(self):
        pass

class Variable(Term):
    def __init__(self, value, next=None):
        self.value=value
        self.next=next

    def __str__(self) -> str:
        if self.next:
            return str(self.value)+"."+str(self.next)
        else:
            return str(self.value)

    def compose(self,M):
        if self.next:
            self.next.compose(M)
        else:
            self.next=M

    def free_values(self):
        return {self.value}
    
    def rename(self,old,new):
        if self.value==old:
            self.value=new
    
    def used_values(self):
        return {self.value}


            

#M is function, N is argument, N will be in []
class Application(Term):
    def __init__(self, location, function, argument):
        self.function=function
        self.argument=argument
        super().__init__(location)

    def __str__(self) -> str:
        return "["+str(self.argument)+"]"+self.location+"."+str(self.function)
    
    def compose(self, M):
        #print("app comp", str(self))
        if self.function:#deal with none parsed as variable
            self.function.compose(M)
        else:
            self.function=M
        #print(str(self))

    def free_values(self):
        return self.argument.free_values()|self.function.free_values()

    def rename(self, old, new):
        self.argument.rename(old,new)
        self.function.rename(old,new)

    def used_values(self):
        return self.argument.used_values()|self.function.used_values()

class Abstraction(Term):
    def __init__(self, location, value, body):
        self.value=value
        self.body=body
        super().__init__(location)

    def __str__(self) -> str:
        return self.location+"<"+self.value+">."+str(self.body)

    def compose(self, M):#this needs to also check something to do with freeness
        if self.value in M.free_values():
            self.rename(self.value, generate_fresh())
        if self.body:
            self.body.compose(M)
        else:
            self.body=M

    def free_values(self):
        return self.body.free_values().discard(self.value)

    def rename(self, old, new):
        if self.value==old:
            self.value=new
        self.body.rename(old,new)

    def used_values(self):
        return self.body.used_values()|{self.value}



def substitute(term, new_term, old_value):#returns rather than works in place
    #print("sub")
    if isinstance(term,Variable):
        #print("into variable")
        if term.value==old_value:
            #print("values are the same")
            new_term.compose(substitute(term.next,new_term,old_value))
            return new_term
        else:
            term.next=substitute(term.next,new_term,old_value)
            return term
    elif isinstance(term,Application):
        term.function=substitute(term.function,new_term,old_value)
        term.argument=substitute(term.argument,new_term,old_value)
        return term
    elif isinstance(term,Abstraction):
        if term.value==old_value:
            return term
        else:
            if new_term==None or term.value not in new_term.free_values():
                term.body=substitute(term.body, new_term, old_value)
                return term
            else:
                term.rename(term.value, generate_fresh())

                return None
    else:
        #print("got to else")
        return None


class State:
    def __init__(self, term) -> None:
        self.term=term
        self.memory={"in":Special_Stack(pop=lambda : Variable(int(input("integer input")))),
                     "out":Special_Stack(append=lambda o: print("output stream: "+str(o))),
                     "rnd": Special_Stack(pop=random.randint(1,100)),#arbitrary to pick 1-100 as range
                     "": []}

    
    def __str__(self) -> str:
        def print_stack(stack):
            stack_string=""
            for t in stack:
                stack_string+=str(t)+", "
            return "["+stack_string[:-2]+"]"

        def print_memory(memory):
            memory_string=""
            for location in memory:
                if location not in ["in", "out", "rnd"]:
                    memory_string+=location+": "+print_stack(memory[location])+",\n"
            return "{"+memory_string[:-2]+"}"
        
        return str(self.term)+"\n"+print_memory(self.memory)


    def step(self):#returns bool of success
        #print(type(self.term))
        if isinstance(self.term,Application):
            if self.term.location in self.memory:
                self.memory[self.term.location].append(self.term.argument)
            else:
                self.memory[self.term.location]=[self.term.argument]
            self.term=self.term.function
            return True
        elif isinstance(self.term,Abstraction):
            #print("hi")
            #print(self.term)
            if self.term.location in self.memory:
                temp=self.memory[self.term.location].pop()
            else:#assumes an empty stack contains infinite Nones
                temp=None
            #print(temp,self.term.value)
            self.term=substitute(self.term.body,temp,self.term.value)
            #print(self.term)
            return True
        elif isinstance(self.term, Variable):#all variables including stack operations
                                             #Evaluating constants at this point is valid however it would be better to do it else where
            #print(self.term.value)
            if self.term.value=="+":#addition, add print etc here? 
                self.memory[""].append(Variable(self.memory[""].pop().value+self.memory[""].pop().value))
            elif self.term.value=="*":
                self.memory[""].append(Variable(self.memory[""].pop().value*self.memory[""].pop().value))
            elif self.term.value=="and":
                self.memory[""].append(Variable(self.memory[""].pop().value and self.memory[""].pop().value))

            elif self.term.value=="if":#warning, without type checking most things other than 0 will be true.
                if self.memory[""].pop():
                    t=self.memory[""].pop()
                    self.memory[""].pop()
                    self.memory[""].append(t)
                else:
                    self.memory[""].pop()
           # elif self.term.value=="while":
                #while N M ~>  [M . while N M] . [] . N . if
            #    M=self.memory[""].pop()
             #   N=self.memory[""].pop()
            elif self.term.value=="print":
                self.memory["out"].append(self.memory[""].pop())
            elif self.term.value=="read":
                self.memory[""].append(self.memory["in"].pop())
            elif self.term.value == "rand":
                self.memory[""].append(self.memory["rnd"].pop())
            elif "get" in self.term.value:
                l=self.term.value.split()
                #if l[0]=="get" way to check it actually is get in the right place.
                t=self.memory[l[1]].pop()
                self.memory[l[1]].append(t)
                self.memory[""].append(t)
            elif "set" in self.term.value:
                l=self.term.value.split()
                #if l[0]=="set" way to check it actually is get in the right place.
                self.memory[l[1]].pop()
                self.memory[l[1]].append(self.memory[""].pop())
            else: 
                print("No step available: Variable ",self.term.value)
                return False
            self.term=self.term.next
            return True
        else:#None case
            print("No step available: None")
            print(self)
            return False
        
    def run(self):
        step_result=True
        while step_result:
            step_result=self.step()
            #print(self)
    

class Special_Stack:
    def __init__(self, pop=None, append=None):
        self.append=append
        self.pop=pop
        
def generate_fresh():
    t=current_state.term
    used=t.used_values()
    valid=POSSIBLEVALUES-used
    return next(iter(valid))

def base_parse(s):
    l=s.split(".")
    #print(l)
    temp=bpr(l)
    #print(temp)
    return temp

def bpr(l):
    if l:
        t=l.pop(0)
        if "<" in t:
            temp=t.split("<")
            location=temp[0]
            value=temp[1][:-1]#getting rid of >
            return Abstraction(location, value, bpr(l))
        elif "[" in t:
            list1=[t[1:]]
            while "]" not in list1[-1]:#this doesn'thandle nesting correctly
                list1.append(l.pop(0))
            
            temp=list1.pop().split("]")
            list1.append(temp[0])
            location=temp[1]
            return Application(location,bpr(l),bpr(list1))
        elif t!="None":
            return Variable(t, bpr(l))
    else:
        return None

def inter_parse(s):
    
    #desired data structure: 
    stack=[]

    for c in s:
        
        if c==")":
            temp_list=[]
            while stack[-1]!="(":
                temp_list.append(stack.pop())
            stack.pop()
            temp_list.reverse()
            stack.append(temp_list)
        else:
            stack.append(c)
    return ipr(stack)

def ipr(l):
    #print(l)
    s=""
    for a in l:
        if isinstance(a, list):
            s+=ipr(a)
        else:
            s+=a
    #do operations here
    def do_operations(s):#str to str
        if ";" in s:
            l=s.split(";")
            #print(l)
            t=base_parse(do_operations(l[0]))
            t.compose(base_parse(do_operations(l[1])))
            return str(t)
        elif ":" in s:
            l=s.split(":=")
            location=l[0]
            value=l[1]
            #print(l)
            return str(Abstraction(location, "_", Application(location,None, base_parse(value))))
            
        elif "=" in s:#some other expressions include = so this must be done after
            l=s.split("=")
            return "["+do_operations(l[1])+"].<"+l[0]+">"
        

        return str(base_parse(s))#should be able to remove both layers
    
           
#Types of operations
#Binary: composition
#Single replace: huh?
#compose: term ; term
#update: location := term
#lookup: ! location

#set: set location
#get: get location
#rand:
#read:
#print
    return do_operations(s)

#print(inter_parse("a:=2;(<x>.!a)(a:=3;0)"))
#print(inter_parse("a:=2;([u].w).<y>.y"))        
#print(inter_parse("(x=N);M"))

    

def run_demo():
    demo="in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out"
    print("First we'll parse this string and use it as starting term:")
    print(demo)
    start_term=base_parse(demo)
    current_state=State(start_term)
    print("Which makes this the starting state, empty stacks and that term")
    print(current_state)
    print("Now doing a single step")
    current_state.step()
    print(current_state)
    print("Running till termination")
    current_state.run()
    print(current_state)
    

def run_second_demo():
    demo="((read;read);+);print"
    print("This time doing the same using keywords instead")
    start_term=base_parse(inter_parse(demo))
    current_state=State(start_term)
    print("hi")
    current_state.run()
    print("hi")
    print(current_state)

    pass
#t1=base_parse("in<x>.c<_>.[x].in<y>.[y]c.[y].+.<p>.[p]out")
#current_state=State(t1)
#current_state.run()
#test=Special_Stack(pop=lambda : int(input("integer input")))
#print(test.pop())
run_demo()
run_second_demo()
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