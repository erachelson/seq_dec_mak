def exercise_model(N=20):
    model = cp_model.CpModel()
    df = pd.Series(range(N))
    X = model.NewBoolVarSeries("X", df.index)
    Y = model.NewBoolVarSeries("Y", df.index[:-1])
    Z = model.NewIntVar(lb=0, ub=2*N, name="Z")
    for i in range(N-1):
        model.Add(X[i]==X[i+1]).OnlyEnforceIf(Y[i])
        model.Add(X[i]!=X[i+1]).OnlyEnforceIf(Y[i].Not())
    for i in range(N-3):
        model.Add(Y[i]!=Y[i+2])
    model.Add(sum(X[::3])+sum(Y)==Z)
    model.Maximize(Z)
    return model, X, Y, Z
