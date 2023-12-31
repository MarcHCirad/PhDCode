import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import csv
from myScheme import rungeKutta4, nonStandardScheme
from myModel import equationFVH



def solveModel(equation, scheme, init, n, dt, param):
    """
    Solve the equation using CI given by init, until time n*dt is reached
    """
    result = np.zeros((n+1, 4))
    result[0] = init
    for ind in range(n):
        result[ind+1][0] = result[ind][0] + dt
        result[ind+1][1:] = scheme(equation, result[ind][1:], dt, param)
    return result

def computeEquilibria(param, equilibria=["VH", "FH", "FVH"]):
    """
    Compute all possible stable equilibria of equationModel
    """
    rV, KV, alpha, muV, lambdaVH = param["rV"], param["KV"], param["alpha"], param["muV"], param["lambdaVH"]
    rF, KF, omega, f, muF, lambdaFH = param["rF"], param["KF"], param["omega"], param["f"], param["muF"], param["lambdaFH"]
    e, muH = param["e"], param["muH"]

    dV = (rV - muV)
    dF = (rF - muF - omega*f)

    rslt = {}
    for eq in equilibria:
        if eq=="VH":
            V_VH = 1/(rV/KV + e*lambdaVH**2/muH)*dV
            H_VH = e*lambdaVH/muH*V_VH
            rslt[eq] = [0, V_VH, H_VH]
        elif eq=="FH":
            F_FH = 1/(rF/KF + e*lambdaFH**2/muH)*dF
            H_FH = e*lambdaFH/muH*F_FH
            rslt[eq] = [F_FH, 0, H_FH]
        elif eq=="FVH":
            V_0 = KV/rV*(dV - lambdaVH/lambdaFH*dF)
            V_1 = lambdaVH/lambdaFH*rF/rV*KV/KF - alpha*KV/rV
            H_0 = dF/lambdaFH
            H_1 = rF/(lambdaFH*KF)
            F_FVH = (muH/e*H_0 - lambdaVH*V_0) / (lambdaFH + lambdaVH*V_1 + muH/e*H_1)
            V_FVH = V_0 + V_1*F_FVH
            H_FVH = H_0 - H_1*F_FVH
            rslt[eq] = [F_FVH, V_FVH, H_FVH]

    return rslt

def stabilityTresholds(param):
    """
    Compute the stabilities tresholds for equationModel
    """
    rV, KV, alpha, muV, lambdaVH = param["rV"], param["KV"], param["alpha"], param["muV"], param["lambdaVH"]
    rF, KF, omega, f, muF, lambdaFH = param["rF"], param["KF"], param["omega"], param["f"], param["muF"], param["lambdaFH"]
    e, muH = param["e"], param["muH"]
    R0V = rV / muV
    R0F = rF / (muF + omega*f)
    TF = (lambdaVH/muV) * (omega*f + muF)/lambdaFH * (R0F - 1) / (R0V - 1) * (1 + muH/(e*lambdaVH**2)*rV/KV)
    TV = (muV/lambdaVH) * lambdaFH/(omega*f + muF) * (R0V - 1) / (R0F - 1) * (1 + muH/(e*lambdaFH**2)*rF/KF) / (1 + alpha*muH/(e*lambdaFH*lambdaVH))

    return {"R_0^V":R0V, "R_0^F":R0F, "T^F":TF, "T^V":TV}

def interpretStabilityTresholds(param):
    """
    Return a string of stable equilibrium
    """
    tresholds = stabilityTresholds(param)
    R0V, R0F, TV, TF = tresholds["R_0^V"], tresholds["R_0^F"], tresholds["T^V"], tresholds["T^F"]
    if (R0V < 1) and (R0F < 1) :
        return "TE"
    elif (R0V > 1) and (R0F > 1) :
        if (TF < 1) and (TV < 1):
            return "VH & FH"
        elif (TF > 1) and (TV > 1):
            return "FVH"
        elif (TF < 1) and (TV > 1):
            return "VH"
        elif (TF > 1) and (TV < 1):
            return "FH"
    elif (R0V > 1) and (R0F < 1):
        if (TF < 1):
            return "VH"
    elif (R0V < 1) and (R0F > 1):
        if (TV < 1):
            return "FH"
    else:
        return ""

def writeResult(filename, resultSimu, param, paramSimu, writeStabilityTresholds=False):
    """
    Write the results on a csv file
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        writer.writerow(['####_Global_Param_####'])
        writer.writerow(list(param.keys()))
        writer.writerow(list(param.values()))
        writer.writerow(["####_Simulation_Param_####"])
        writer.writerow(list(paramSimu.keys()))
        writer.writerow(list(paramSimu.values()))

        if writeStabilityTresholds:
            writer.writerow(["####_Stability_Tresholds_####"])
            stabilityCond = stabilityTresholds(param)
            writer.writerow(list(stabilityCond.keys()))
            writer.writerow(list(stabilityCond.values()))

        writer.writerow(["############"])
        writer.writerow(["Time", "F", "V", "H"])
        for result in resultSimu:
            writer.writerow([result[0], result[1], result[2], result[3]])

def plotVectorField(equationModel, listEquilibrium, listNameEquilibrium, param, box, step):
    """
    Plot a vector field. Dimensions of the plot are given by
    box parameters (format [Fmin, Fmax, Vmin, Vmax, Hmin, Hmax]) 
    step parameter indicates the step between two coordinates
    """
    coord_F = np.arange(box[0], box[1], step)
    coord_V = np.arange(box[2], box[3], step)
    coord_H = np.arange(box[4], box[5], step)
    x, y, z = np.meshgrid(coord_F, coord_V, coord_H, indexing='ij')
    dF = np.zeros((len(coord_F), len(coord_V), len(coord_H)))
    dV = np.zeros((len(coord_F), len(coord_V), len(coord_H)))
    dH = np.zeros((len(coord_F), len(coord_V), len(coord_H)))

    for ind_F in range(len(coord_F)):
        for ind_V in range(len(coord_V)):
            for ind_H in range(len(coord_H)):
                val = equationModel([coord_F[ind_F], coord_V[ind_V], coord_H[ind_H]], param)
                dF[ind_F, ind_V, ind_H] = val[0]
                dV[ind_F, ind_V, ind_H] = val[1]
                dH[ind_F, ind_V, ind_H] = val[2]
    
    ax = plt.figure().add_subplot(projection='3d')
    ax.quiver(x, y, z, dF, dV, dH, normalize=True, length=1)
    
    for equilibrium, nameEquilibrium in zip(listEquilibrium, listNameEquilibrium):
        [F, V, H] = equilibrium
        ax.plot(F, V, H, label=r'$%s$'%nameEquilibrium, marker='x', color = 'red', linestyle='')

    ax.set(xlabel='F', ylabel='V', zlabel='H')
    ax.legend()
    plt.show()

def plotResult(listEquilibrium, listNameEquilibrium, listResult, labelResult):
    """
    Plot trajectories of given solutions
    """
    ax = plt.figure().add_subplot(projection="3d")
    for result, label in zip(listResult, labelResult):
        ax.plot(result[:,1], result[:,2], result[:,3], linestyle='-', label=label)

    for equilibrium, nameEquilibrium in zip(listEquilibrium, listNameEquilibrium):
        [F, V, H] = equilibrium
        ax.plot(F, V, H, label=r'$%s$'%nameEquilibrium, marker='o', linestyle='')
        
    ax.set(xlabel='F', ylabel='V', zlabel='H')
    ax.legend()
    plt.show()
    
def plotDiagramBifurcation(param, listCoordLambdaVH, listCoordLambdaFH):
    """
    Plot a diagram of bifurcation in \lambda_FH \lambda_VH plane 
    """
    x, y = np.meshgrid(listCoordLambdaVH, listCoordLambdaFH, indexing='ij')
    dicStabilityNbr = {"FVH":0, "VH":1, "FH":2, "VH & FH":3}
    vecStability = np.zeros((len(listCoordLambdaVH)-1, len(listCoordLambdaFH)-1))

    listLambdaVH = [(listCoordLambdaVH[k+1]+listCoordLambdaVH[k])/2 for k in range(len(listCoordLambdaVH)-1)]
    listLambdaFH = [(listCoordLambdaFH[k+1]+listCoordLambdaFH[k])/2 for k in range(len(listCoordLambdaFH)-1)]

    for ind_V in range(len(listLambdaVH)):
        for ind_F in range(len(listLambdaFH)):
            param["lambdaFH"] = listLambdaFH[ind_F]
            param["lambdaVH"] = listLambdaVH[ind_V]
            stab = interpretStabilityTresholds(param)
            vecStability[ind_V, ind_F] = dicStabilityNbr[stab]

    fig, ax = plt.subplots()
    cmap = ListedColormap(['r', 'g', 'b', 'k'])
    BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    im = ax.pcolormesh(y, x, vecStability, cmap=cmap, vmin=-0.5, vmax=3.5)
    ax.set(ylabel = r'$\lambda_{VH}$', xlabel = r"$\lambda_{FH}$")
    mcolorbar = fig.colorbar(im)
    mcolorbar.set_ticks([0, 1, 2, 3])
    mcolorbar.set_ticklabels([r"$EE^{FVH}$", r"$EE^{VH}$", r"$EE^{FH}$", r"$EE^{VH} & EE^{FH}$"])
    plt.show()

    return

def plotHistoBifurcation(param, listCoordLambdaVH, listCoordLambdaFH, step, variable):
    """
    Plot a diagram of bifurcation in \lambda_FH \lambda_VH plane 
    """

    dicStabilityColor = {"FVH":'r', "VH":'g', "FH":'b', "VH & FH":'k'}
    vecHeight = np.zeros((len(listCoordLambdaVH)-1, len(listCoordLambdaFH)-1))
    vecWidth = np.zeros((len(listCoordLambdaVH)-1, len(listCoordLambdaFH)-1))
    vecColor = np.zeros((len(listCoordLambdaVH)-1, len(listCoordLambdaFH)-1), dtype='str')

    listLambdaVH = [(listCoordLambdaVH[k+1]+listCoordLambdaVH[k])/2 for k in range(len(listCoordLambdaVH)-1)]
    listLambdaFH = [(listCoordLambdaFH[k+1]+listCoordLambdaFH[k])/2 for k in range(len(listCoordLambdaFH)-1)]
    x, y = np.meshgrid(listLambdaVH, listLambdaFH, indexing='ij')

    for ind_V in range(len(listLambdaVH)):
        for ind_F in range(len(listLambdaFH)):
            param["lambdaFH"] = listLambdaFH[ind_F]
            param["lambdaVH"] = listLambdaVH[ind_V]
            stab = interpretStabilityTresholds(param)

            if stab == "VH & FH":
                eqs = computeEquilibria(param, ["VH", "FH"])
                if variable=="H":
                    height = min(eqs["FH"][2], eqs["VH"][2])
                elif variable=="V":
                    height = min(eqs["FH"][1], eqs["VH"][1])
                elif variable=="F":
                    height = min(eqs["FH"][0], eqs["VH"][0])
                elif variable=="(F+V+H)":
                    height = min(sum(eqs["FH"]), sum(eqs["VH"]))
            else:
                    eq = computeEquilibria(param, [stab])[stab]
                    if variable=="H":
                        height = eq[2]
                    elif variable=="V":
                        height = eq[1]
                    elif variable=="F":
                        height = eq[0]
                    elif variable=="(F+V+H)":
                        height = eq[0]+eq[1]+eq[2]
                

            vecHeight[ind_V, ind_F] = height
            vecWidth[ind_V, ind_F] = step
            vecColor[ind_V, ind_F] = dicStabilityColor[stab]

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    cmap = ListedColormap(['r', 'g', 'b', 'k'])
    BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    
    argmaxHeight = np.unravel_index(np.argmax(vecHeight, axis=None), vecHeight.shape)
    lambdaVHMax, lambdaFHMax = x[argmaxHeight], y[argmaxHeight]
    print("Max value is : ", vecHeight[argmaxHeight], "and it is obtained for lambda_VH = ", lambdaVHMax, "and lambdaFH = ", lambdaFHMax)
    argminHeight = np.unravel_index(np.argmin(vecHeight, axis=None), vecHeight.shape)
    lambdaVHMin, lambdaFHMin = x[argminHeight], y[argminHeight]
    print("Min value is : ", vecHeight[argminHeight], "and it is obtained for lambda_VH = ", lambdaVHMin, "and lambdaFH = ", lambdaFHMin)

    im = ax.bar3d(y.ravel(), x.ravel(), 0, vecWidth.ravel(), vecWidth.ravel(), vecHeight.ravel(), color=vecColor.ravel(), cmap=cmap)
    
    zstring = "$" + variable + "^*$"
    ax.set(ylabel = r'$\lambda_{VH}$', xlabel = r"$\lambda_{FH}$", zlabel=r"%s"%zstring)
    mcolorbar = fig.colorbar(im, boundaries = [-0.5, 0.5, 1.5, 2.5, 3.5], values = [0,1,2,3])
    mcolorbar.set_ticks([0, 1, 2, 3])
    mcolorbar.set_ticklabels([r"$EE^{FVH}$", r"$EE^{VH}$", r"$EE^{FH}$", r"$EE^{VH} & EE^{FH}$"])
    plt.show()

    return

def main():

    ## Param given by Yatat, 2021
    # param = {"rV":1.8, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.8}
    
    # ## Param for VH stable
    # paramVH = {"rV":1.8, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":1, "f":5, "muF":0.1, "e":0.8}
    # paramVH["muH"] = 0.01
    # paramVH["lambdaVH"] = 0.1
    # paramVH["lambdaFH"] = 0.1
    # print(stabilityTresholds(paramVH))
    # print(interpretStabilityTresholds(paramVH))

    # t0, tf = 0., 2000.
    # n = 40000
    # dt = (tf-t0)/n
    # eqs = computeEquilibria(paramVH, ["VH"])
    # F, V, H = eqs["VH"][0], eqs["VH"][1], eqs["VH"][2]
    # F0, V0, H0 = F-F, V+10, H - H
    # init = np.array([t0, F0, V0, H0])
    # resultSimu = solveModel(equationModel, init, n, dt, paramVH)
    # plotResult([eqs["VH"]], ["EE^{VH}"], [resultSimu])

    # ## Param for FVH stable
    paramFVH = {"rV":2, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.8}
    paramFVH["muH"] = 0.01
    paramFVH["lambdaVH"] = 0.332
    paramFVH["lambdaFH"] = 0.1
    paramFVH["H0"] = 20
    eqs = computeEquilibria(paramFVH)

    eq0 = computeEquilibria(paramFVH, ["FVH"])

    print(interpretStabilityTresholds(paramFVH))
    t0, tf = 0., 500.
    n = 5000
    dt = (tf-t0)/n
    print(dt)
    F, V, H = eq0["FVH"][0], eq0["FVH"][1], eq0["FVH"][2]
    F0, V0, H0 = F +8, V+10, H +5
    init = np.array([t0, F0, V0, H0])

    resultSimuFVHRK4 = solveModel("FVH", rungeKutta4, init, 100*n, dt/100, paramFVH)
    resultSimuFVH = solveModel("FVH", nonStandardScheme, init, n, dt, paramFVH)
    resultSimuRVRK4 = solveModel("rV", rungeKutta4, init, 10*n, dt/10, paramFVH)
    resultSimuRV = solveModel("rV", nonStandardScheme, init, n, dt, paramFVH)
    plotResult([eq for eq in list(eqs.values())], [nameEq for nameEq in eqs.keys()], [resultSimuFVH, resultSimuRV, resultSimuRVRK4, resultSimuFVHRK4], ["FVHNSS", "rVNSS", "rVRK4", "FVHRK4"])

    # writeResult("FVH.csv", resultSimuRH, paramFVH, {"dt":dt, "tf":tf, "F0:":F0, "V0": V0, "H0":H0}, True)

    # # ## Param for FH stable
    # paramFH = {"rV":1.8, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.8}
    # paramFH["muH"] = 0.01
    # paramFH["lambdaVH"] = 0.1
    # paramFH["lambdaFH"] = 0.01
    # print(stabilityTresholds(paramFH))
    # print(interpretStabilityTresholds(paramFH))

    # ### Param for FH and VH stable
    # paramVHFH = {"rV":1.8, "KV":19.9, "alpha":0.1, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.8}
    # paramVHFH["muH"] = 0.01
    # paramVHFH["lambdaVH"] = 0.83
    # paramVHFH["lambdaFH"] = 0.25
    # print(stabilityTresholds(paramVHFH))
    # print(interpretStabilityTresholds(paramVHFH))

    # ### Trajectories of solution
    # t0, tf = 0., 200.
    # n = 20000
    # dt = (tf-t0)/n
    # eqs = computeEquilibria(paramVHFH, ["VH", "FH"])
    # F, V, H = 0, 0.03, 2

    # F0, V0, H0 = F, V+4, H+3
    # F1, V1, H1 = 0.03, V+2, H-1
    # F2, V2, H2 = 0.3, 0.2, H+1
    # F3, V3, H3 = 1, 1, 1
    
    # init = np.array([t0, F0, V0, H0])
    # init1 = np.array([t0, F1, V1, H1])
    # init2 = np.array([t0, F2, V2, H2])
    # init3 = np.array([t0, F3, V3, H3])
    # resultSimu = solveModel(equationModel, init, n, dt, paramVHFH)
    # resultSimu1 = solveModel(equationModel, init1, n, dt, paramVHFH)
    # resultSimu2 = solveModel(equationModel, init2, n, dt, paramVHFH)
    # resultSimu3 = solveModel(equationModel, init3, n, dt, paramVHFH)
    
    # plotResult([eqs["VH"], eqs["FH"]], ["EE^{VH}", "EE^{FH}"], [resultSimu, resultSimu1, resultSimu2, resultSimu3])

    # param = {"rV":1.8, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.8}
    
    
    ### Bifurcation diagram
    # paramBifurcation = {"rV":1.8, "KV":19.9, "alpha":0.01, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.1, "f":1, "muF":0.1, "e":0.9}
    # paramBifurcation["muH"] = 0.1

    # paramBifurcation = {"rV":1.8, "KV":50, "alpha":0.02, "muV":0.2, "rF":1.91, "KF":429.2, "omega":0.2, "f":0.5, "muF":0.1, "e":0.9}
    # paramBifurcation["muH"] = 0.3

    # paramBifurcation = {"rV":1.8, "KV":50, "alpha":0.02, "muV":0.1, "rF":0.71, "KF":429.2, "omega":0.5, "f":0.25, "muF":0.1, "e":0.9}
    # paramBifurcation["muH"] = 0.3
    
    # # listLambdaVH = np.arange(0,0.2, 0.001)
    # # listLambdaFH = np.arange(0,0.2, 0.001)
    # # plotDiagramBifurcation(paramBifurcation, listLambdaVH, listLambdaFH)

    # step = 0.01
    # listLambdaVH = np.arange(0,1, step)
    # listLambdaFH = np.arange(0,1, step)
    # plotHistoBifurcation(paramBifurcation, listLambdaVH, listLambdaFH, step, "H")

    return

if __name__ == "__main__":
    main()
