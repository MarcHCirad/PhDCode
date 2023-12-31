import numpy as np
from myModel import equationFVH, equationRV

def rungeKutta4(equationName, variables, dt, param):
    """
    Apply RK4 method over dt using equation function
    """
    if equationName == "FVH":
        k1 = equationFVH(variables, param)
        k2 = equationFVH(variables + dt/2*k1, param)
        k3 = equationFVH(variables + dt/2*k2, param)
        k4 = equationFVH(variables + dt*k3, param)
    elif equationName == "rV":
        k1 = equationRV(variables, param)
        k2 = equationRV(variables + dt/2*k1, param)
        k3 = equationRV(variables + dt/2*k2, param)
        k4 = equationRV(variables + dt*k3, param)

    return variables + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def nonStandardScheme(equationName, variables, dt, param):
    """
    Apply the non standard scheme, as defined in notebook, to equation
    """
    F, V, H = variables[0], variables[1], variables[2]

    rV, KV, alpha, muV, lambdaVH = param["rV"], param["KV"], param["alpha"], param["muV"], param["lambdaVH"]
    rF, KF, omega, f, muF, lambdaFH = param["rF"], param["KF"], param["omega"], param["f"], param["muF"], param["lambdaFH"]
    e, muH = param["e"], param["muH"]

    deltaF = rF - muF - omega*f
    deltaV = rV - muV

    if equationName == "FVH":
        phiF = (np.exp(deltaF*dt) - 1)/deltaF
        phiV = (np.exp(deltaV*dt) - 1)/deltaV
        phiH = dt
        Fdt = F*(1 + phiF*deltaF) / (1 + rF/KF * phiF * F + lambdaFH * phiF * H)
        Vdt = V*(1 + phiV*deltaV) / (1 + rV/KV * phiV * V + alpha * phiV * F + lambdaVH * phiV * H)
        Hdt = H*(1 + phiH * e * (lambdaFH * Fdt + lambdaVH * Vdt)) / (1 + muH * phiH * H)
    
    elif equationName == "rV":
        H0 = param["H0"]
        rVH = rV*H/(H+H0)
        phiF = (np.exp(deltaF*dt) - 1)/deltaF
        phiV = (np.exp((rV - muV)*dt) - 1)/deltaV
        phiH = dt
        
        Fdt = Fdt = F*(1 + phiF*deltaF) / (1 + rF/KF * phiF * F + lambdaFH * phiF * H)
        Vdt = Vdt = V*(1 + phiV*(rVH - muV)) / (1 + rVH/KV * phiV * V + alpha * phiV * F + lambdaVH * phiV * H)
        Hdt = H*(1 + phiH * e * (lambdaFH * Fdt + lambdaVH * Vdt)) / (1 + muH * phiH * H)

    return np.array([Fdt, Vdt, Hdt])