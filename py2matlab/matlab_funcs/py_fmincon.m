function out = py_fmincon(cost, x0, A, b, Aeq, beq, lb, ub, nonlinineq, nonlineq, variables, options)
func = matlabFunction(cost, 'Vars', {variables});
if isempty(nonlinineq)
    inequalities = matlabFunction(nonlinineq, 'Vars', variables);
else
    inequalities = matlabFunction(nonlinineq, 'Vars', {variables});
end

if isempty(nonlineq)
    equalities = matlabFunction(nonlineq, 'Vars', variables);
else
    equalities = matlabFunction(nonlineq, 'Vars', {variables});
end

nonlcon = @(x)(deal(inequalities(x), equalities(x)));

out = fmincon(func, x0, A, b, Aeq, beq, lb, ub, nonlcon, options);
end