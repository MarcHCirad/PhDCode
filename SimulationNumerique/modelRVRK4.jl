include("modelRV.jl")
struct RVRK4 <: numericalModel

    mathModel::modelRV

    t0::Float64
    tf::Float64
    dt::Float64
    n::Int64

    result::Matrix{Float64}

    function RVRK4(modelParam::Dict{String, Float64}, numericalParam::Dict{String, Float64}, initialValues::Dict{String, Float64})
        mathModel = modelRV(modelParam)

        t0, tf, dt = numericalParam["t0"], numericalParam["tf"], numericalParam["dt"]
        n = Int((tf-t0)/dt)
        
        result = Matrix{Float64}(undef, 4, n+1)
        result[:,1] = [t0, initialValues["F0"], initialValues["V0"], initialValues["H0"]]

        new(mathModel, t0, tf, dt, n, result)
    end

    function RVRK4(mathModel::modelRV, numericalParam::Dict{String, Float64}, initialValues::Dict{String, Float64})
        t0, tf, dt = numericalParam["t0"], numericalParam["tf"], numericalParam["dt"]
        n = Int((tf-t0)/dt)
        
        result = Matrix{Float64}(undef, 4, n+1)
        result[:,1] = [t0, initialValues["F0"], initialValues["V0"], initialValues["H0"]]

        new(mathModel, t0, tf, dt, n, result)
    end
end

function numericalScheme(model::RVRK4, variables::Vector{Float64})
    k1 = equationModel(model.mathModel, variables)
    k2 = equationModel(model.mathModel, variables + model.dt/2 * k1)
    k3 = equationModel(model.mathModel, variables + model.dt/2 * k2)
    k4 = equationModel(model.mathModel, variables + model.dt * k3)

    return variables + model.dt/6*(k1 + 2*k2 + 2*k3 + k4)
end

function solveModel(model::RVRK4)
    for ind in 1:model.n
        model.result[1, ind+1] = model.result[1, ind] + model.dt
        model.result[2:4, ind+1] = numericalScheme(model, model.result[2:4, ind])
    end
end
