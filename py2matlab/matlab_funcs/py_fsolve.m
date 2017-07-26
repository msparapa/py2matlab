function out = py_fsolve(expression, x0, variables, options)
    func = matlabFunction(expression, 'Vars', {variables});
    out = fsolve(func, x0, options);
end