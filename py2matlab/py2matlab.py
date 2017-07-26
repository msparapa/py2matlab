from sympy import sympify, Symbol
import matlab.engine as matlab
import numpy as np
import os

class py2matlab(object):
    eng = []

    def __init__(self, eng=[]):
        if eng == []:
            self.eng = matlab.start_matlab()
            self.eng.eval('addpath(genpath(\'' + os.path.dirname(os.path.abspath(__file__)) + '/\'))')
            self.eng.workspace['options'] = self.eng.optimset('Display', 'off')
        else:
            pass

    def close(self):
        self.eng.quit()

    def sympy2mup(self, name='symexpr', expr=[]):
        expr = str(expr)
        expr = expr.replace('**','^')
        self.eng.workspace[name] = self.eng.eval(expr)
        return Symbol(name)

    def mup2sympy(self, expr=[], variables=[]):
        pass

    def fmincon(self, cost=[], x0=[], A=[], b=[], Aeq=[], beq=[], lb=[], ub=[], nonlinineq=[], nonlineq=[], variables=[]):
        numequations = len(cost)
        numvariables = len(variables)
        if x0 == []:
            x0 = np.zeros(numequations)

        self.eng.workspace['varset'] = self.eng.eval('[]')
        for ii in variables:
            self.eng.workspace[str(ii)] = self.eng.sym(str(ii))
            self.eng.workspace['varset'] = self.eng.eval('[varset, ' + str(ii) + ']')

        equationset = [self.sympy2mup(name='fminconfunc', expr=cost[0])]

        nonlconA = []
        nonlconB = []

        for index, val in enumerate(nonlineq):
            nonlconB.append(self.sympy2mup(name='nonlconB' + str(index), expr=val))

        self.eng.workspace['ans'] = self.eng.eval('py_fmincon(' + str(equationset) + ', ' + str(x0).replace('\n','') + ', [], [], [], [], [], [], [], ' + str(nonlconB) + ', ' + str(variables) + ', options);')
        # np.array_str(x0, max_line_width=1000000)
        result = [self.eng.eval('ans(' + str(ii + 1) + ')') for ii in range(numvariables)]
        out = dict(zip(variables, result))

        return out


    def fsolve(self, equations=[], x0=[], variables=[]):

        numequations = len(equations)
        numvariables = len(variables)

        if x0 == []:
            x0 = np.zeros(numequations)

        self.eng.workspace['varset'] = self.eng.eval('[]')
        for ii in variables:
            self.eng.workspace[str(ii)] = self.eng.sym(str(ii))
            self.eng.workspace['varset'] = self.eng.eval('[varset, ' + str(ii) + ']')

        equationset = [self.sympy2mup(name='fsolvefunc' + str(index), expr=val) for index, val in enumerate(equations)]

        self.eng.workspace['ans'] = self.eng.eval('py_fsolve(' + str(equationset) + ', ' + str(x0) + ', ' + str(variables) + ', options);')

        result = [self.eng.eval('ans(' + str(ii + 1) + ')') for ii in range(numvariables)]
        out = dict(zip(variables, result))

        return out


    def solve(self, equations=[], variables=[], auxvars=[]):

        auxvars = set(auxvars)
        numequations = len(equations)
        numvariables = len(variables)

        for ii in range(numequations):
            auxvars = auxvars.union(equations[ii].free_symbols)

        auxvars = list(auxvars)

        for ii in range(numvariables):
            auxvars = [x for x in auxvars if x != variables[ii]]

        for ii in variables + auxvars:
            self.eng.workspace[str(ii)] = self.eng.sym(str(ii))

        self.eng.workspace['ans'] = self.eng.eval('solve(' + str(equations).replace('**','^') + ', ' + str(variables) + ')')

        result = []
        for ii in range(numvariables):

            if len(variables) > 1:
                resultSet = []
                for jj in range(int(self.eng.eval('length(ans.' + str(variables[ii]) + ')'))):
                    resultSet.append(sympify(self.eng.char(self.eng.eval('ans.' + str(variables[ii]) + '(' + str(jj + 1) + ')')).replace('^','**')))

            else:
                resultSet = []
                for jj in range(int(self.eng.eval('length(ans)'))):
                    resultSet.append(sympify(self.eng.char(self.eng.eval('ans' + '(' + str(jj+1) + ')')).replace('^','**')))

            for jj in range(len(resultSet)):
                free = list(resultSet[jj].free_symbols)
                strauxvars = []
                for kk in auxvars:
                    strauxvars.append(str(kk))

                order = []
                for kk in free:
                    if str(kk) in strauxvars:
                        order.append(strauxvars.index(str(kk)))

                sortedaux = []
                for kk in order:
                    sortedaux.append(auxvars[kk])

                resultSet[jj] = resultSet[jj].subs(dict(zip(free, sortedaux)), simultaneous=True)

            result.append(resultSet)

        out = dict(zip(variables,result))

        return out