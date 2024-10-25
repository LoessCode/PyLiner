import matplotlib.pyplot as plt
import numpy as np
import math

global parameters
parameters = {
    'π': math.pi,
    'e': math.e
}
def set_equation_params(params: dict):
    global parameters
    parameters = params

#Numbers
class __Term():
    def __init__(self, number: str):
        if number[0].isdigit():
            self.value = float(number)
            self.operator = '+'
        else:
            self.value = -float(number[1:]) if '-' in number else float(number[1:])
            self.operator = number[0]
        
    def evaluate(self, x: float) -> float:
        return self.value
    
    def __repr__(self):
        return self.operator + str(self.value)

#Variable x
class __Term_x():
    def __init__(self, term: str):
        
        self.operator = term[0]
        
    def evaluate(self, x: float) -> float:
        return x
    
    def __repr__(self):
        return self.operator + 'x'
#Other Parameters
class __Term_parameter():
    def __init__(self, term: str):
        self.operator = term[0]
        self.parameterCharacter = term[1]
        
    def evaluate(self, x: float) -> float:
        if self.parameterCharacter in parameters.keys():
            return parameters[self.parameterCharacter]
        else:
            parameters[self.parameterCharacter] = 10
            return parameters[self.parameterCharacter]
    
    def __repr__(self):
        return self.operator + self.parameterCharacter

#Trigonometric Functions
class __Term_trig():
    def __init__(self, term: str, argumentEquation: list):
        self.functionType = term[2:]
        self.argumentEquation = argumentEquation
        self.operator = term[1]
        
    def evaluate(self, x: float):
        arg = evaluate_final(self.argumentEquation, x)
        try:
            if self.functionType == 'sin':
                return math.sin(arg)
            elif self.functionType == 'cos':
                return math.cos(arg)
            elif self.functionType == 'tan':
                return math.tan(arg)
            elif self.functionType == 'cot':
                return 1/math.tan(arg)
            elif self.functionType == 'sec':
                return 1/math.cos(arg)
            elif self.functionType == 'cosec':
                return 1/math.sin(arg)
            else:
                if self.functionType == 'arcsin':
                    try:
                        return math.asin(arg)
                    except:
                        return math.pi/2 if arg > 0 else -math.pi/2
                elif self.functionType == 'arccos':
                    try:
                        return math.acos(arg)
                    except:
                        return math.pi if arg < -1 else 0
                elif self.functionType == 'arctan':
                    return math.atan(arg)
                elif self.functionType == 'arccot':
                    return math.pi/2 - math.atan(arg)
                elif self.functionType == 'arcsec':
                    try:
                        return math.acos(1/arg)
                    except:
                        return 9999999 if arg < 0 else -9999999
                elif self.functionType == 'arccosec':
                    try:
                        return math.asin(1/arg)
                    except:
                        return -9999999 if arg < 0 else 9999999
        except ZeroDivisionError:
            return 99999999999
          
    def __repr__(self):
        return self.operator + self.functionType + '(' + " ".join([i.__repr__() for i in self.argumentEquation]) + ')'

#Brackets
class __Term_brac():
    def __init__(self, term: str, nestedEquation: list):
        self.nestedEquation = nestedEquation
        self.operator = term[1]
        
    def evaluate(self, x: float):
        return evaluate_final(self.nestedEquation, x)
    
    def __repr__(self):
        return self.operator + '(' + " ".join([i.__repr__() for i in self.nestedEquation]) + ')'
class __Term_log():
    def __init__(self, term: str, nestedEquation: list):
        self.argumentEquation = nestedEquation
        self.operator = term[1]
        
    def evaluate(self, x: float):
        try:
            return math.log(evaluate_final(self.argumentEquation, x), parameters['e'])
        except:
            return -999999999
    
    def __repr__(self):
        return 'log'+ self.operator + '(' + " ".join([i.__repr__() for i in self.argumentEquation]) + ')'

#Function to check if string is a float
#Example: "1.293"
def __is_float(number: str) -> bool:
    try:
        float(number)
        return True
    except:
        return False

#Function to break down input string
def __interpret_string(inputString: str) -> dict:
    print("INPUT --> ", inputString)
    functionTree = {}
    treeIndex = [0]
    buffer = ""

    for inputStringIndex, inputStringChar in enumerate(inputString):
        print('{',buffer,'} @ ', treeIndex, ' ---> ', functionTree, sep='')
        
        
        if inputStringChar == '(':
            isNotFunction = True
            for inputStringChar in buffer:
                if inputStringChar.isalpha():
                    isNotFunction = False
            #If it is bracket
            if isNotFunction:
                operator = '+'
                if buffer == '':
                    operator = '+'
                
                else:
                    functionTree[str(treeIndex)] = ('' if buffer[0] in '+-*/^' else '+') + buffer.strip()
                    treeIndex[-1] += 1
                    if buffer[0] in '+-*/^':
                        if len(buffer) == 1:
                            operator = buffer[0]
                        else:
                            operator = '*'
                    elif __is_float(buffer):
                        operator = '*'
                treeIndex.append(0)
                    
                functionTree[str(treeIndex)] = "$" + operator + "brac"
                buffer = ""
                treeIndex[-1] += 1
                
            #If it is a function
            else:
                print(buffer)
                treeIndex[-1] += 1
                treeIndex.append(0)
                if buffer[0].isalpha():
                    functionTree[str(treeIndex)] = "$+"+buffer.strip()
                else:
                    functionTree[str(treeIndex)] = "$"+buffer.strip()
                buffer = ""
                treeIndex[-1] += 1
            
        #Closing brackets
        elif inputStringChar == ')':
            if buffer != '':
                functionTree[str(treeIndex)] = buffer.strip()        
            treeIndex.pop()
            treeIndex[-1] += 1
            buffer = ""
            
        #Handling operators
        elif inputStringChar in ('+', '-', '/', '*', '^'):
            if buffer != '':
                functionTree[str(treeIndex)] = ('' if buffer[0] in '+-*/^' else '+') + buffer.strip()
                buffer = inputStringChar
                treeIndex[-1] += 1
            else:
                buffer = inputStringChar
        
        #Handling variable x
        elif (inputStringChar.isalpha() and 
              (__is_float(buffer) or __is_float(buffer[1:]) or buffer in  ('+', '-', '/', '*', '^') or buffer == '') and 
              not inputString[inputStringIndex+1:inputStringIndex+2].isalpha()):
            
            if buffer in  ('+', '-', '/', '*', '^'):
                functionTree[str(treeIndex)] = buffer + inputStringChar
                buffer = ""
                treeIndex[-1] += 1
            else:
                if buffer != '':
                    functionTree[str(treeIndex)] = buffer
                    treeIndex[-1] += 1
                    functionTree[str(treeIndex)] = '*' + inputStringChar
                    treeIndex[-1] += 1
                else:
                    functionTree[str(treeIndex)] = '+' + inputStringChar
                    treeIndex[-1] += 1
                buffer = ""
            
        #If no token found, character added to buffer
        else:
            buffer += inputStringChar.strip()
    if buffer != '':
        functionTree[str(treeIndex)] = buffer.strip()
    print("FUNC --> ", functionTree)
    return functionTree

#Function that takes broken down input and converts to class objects
def __interpret_dict(functionTree: dict) -> list:
    resultTerms = []
    
    #Specifies if function is recursion or is initial call
    isRecursion = False
    if '[]' in functionTree.keys():
        isRecursion = True
    
    #To prevent stack overflow
    blacklistedTreeIndices = []
    for treeIndex, term in functionTree.items():
        treeIndex = eval(treeIndex)
        
        if treeIndex != [] and treeIndex not in blacklistedTreeIndices:
            #If there is bracket or function
            if treeIndex != [0] and treeIndex[-1] == 0:
                nestedEquation = {}
                
                #Calling self for nested equations
                for treeIndex1, term1 in functionTree.items():
                    treeIndex1 = eval(treeIndex1)
                    
                    if len(treeIndex1) >= len(treeIndex):
                        if treeIndex1[:len(treeIndex)-1] == treeIndex[:len(treeIndex)-1]:
                            if treeIndex1 == treeIndex:
                                nestedEquation['[]'] = term
                            else:
                                nestedEquation[str(treeIndex1)] = term1
                resultTerms.append(__interpret_dict(nestedEquation))
        
                #Adding terms inside brackets to blacklist
                for treeIndex1, term1 in functionTree.items():
                    treeIndex1 = eval(treeIndex1)
                    if treeIndex1 != []: 
                        if treeIndex1[0] == treeIndex[0]:
                            blacklistedTreeIndices.append(treeIndex1)
            else:
                if __is_float(term[1:]):
                    resultTerms.append(__Term(term))
                elif __is_float(term):
                    resultTerms.append(__Term('+'+term))
                elif term[-1].isalpha() and not term[0].isalpha():
                    if term[-1] == 'x':
                        resultTerms.append(__Term_x(term))
                    else:
                        resultTerms.append(__Term_parameter(term))
        print('TBASE --> ', resultTerms, ' w/ ', isRecursion, blacklistedTreeIndices)
    

    if not isRecursion: 
        return resultTerms
    else:
        keyword = functionTree['[]'][2:]
        term = functionTree['[]']
        print('T_TERM -> ', term, '~', resultTerms)
        if (keyword in ('sin', 'cos', 'tan', 'cot', 'sec', 'cosec') or 
        keyword[3:] in  ('sin', 'cos', 'tan', 'cot', 'sec', 'cosec')):
            
            return(__Term_trig(term, resultTerms))
        elif keyword in ('log', 'ln'):

            return(__Term_log(term, resultTerms))

        elif keyword == "brac":
            
            return(__Term_brac(term, resultTerms))   

#Function that accepts class objects and,
#evaluates to give float answer
def evaluate_final(fun, x:float) -> float:
    
    termValues = []

    for termObject in fun:
        if termObject.operator not in '*/^':
                termValues.append(termObject.evaluate(x))
        else:
            try:
                lastValue = termValues.pop()
            except: 
                lastValue = 1
            if termObject.operator == '/':
                termValues.append(lastValue/termObject.evaluate(x))
            elif termObject.operator == '*':
                termValues.append(lastValue*termObject.evaluate(x))
            elif termObject.operator == '^':
                termValues.append(lastValue**termObject.evaluate(x))
   
    return sum(termValues)

#Called by the main app
def parse(inputString: str) -> list:
    return __interpret_dict(
        __interpret_string(
            inputString
        )
    )

def val(termObjects: list, x: float) -> float:
    return evaluate_final(termObjects, x)
    