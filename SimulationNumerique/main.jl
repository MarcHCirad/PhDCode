t = @elapsed begin

include("modelFVHRK4.jl")
include("modelFVHNSS.jl")
include("modelRVRK4.jl")
include("modelRVNSS.jl")
include("plotFile.jl")

function main()
    ## Model parameters
    paramFVH = Dict([("rV",1.0), ("KV",50.9), ("alpha",0.01), ("muV",0.1), ("rF",0.71), ("KF",429.2), ("omega",0.1), ("f",0.0), ("muF",0.1), ("e",0.8)])
    paramFVH["H0"] = 0.01
    paramFVH["muH"] = 0.01
    paramFVH["lambdaVH"] = 0.0332
    paramFVH["lambdaFH"] = 0.01
    
    ## Create a mathematical model
    myMathModel = modelFVH(paramFVH)

    step = 0.001
    stop = 0.2
    listLambdaVH = Vector(range(step, stop, step=step))
    listLambdaFH = Vector(range(step, stop, step=step))

    ## Compute a bifurcation diagram and write it in a csv file
    computeBifurcationDiagram(myMathModel, listLambdaFH, listLambdaVH, "bifurcationDiagram.csv")
    ## Plot a bifurcation diagram from a csv file
    plotBifurcationFile("bifurcationDiagram.csv", "bifurcationDiagram.html"; toPlot=true)

    # ## Numerical parameters
    # t0, tf = 0., 500.
    # n = 50000
    # dt = (tf-t0)/n
    # numericalParam = Dict([("t0", t0), ("tf", tf), ("dt", dt)])

    # F0, V0, H0 = 8.,10.,5.
    # initialValues = Dict([("F0", F0), ("V0", V0), ("H0", H0)])

    # ## Create a numerical model 
    # myModel = RVNSS(paramFVH, numericalParam, initialValues)
    # solveModel(myModel)
    # CSV.write("test.csv", Tables.table(transpose(myModel.result)))
end

main()

end
println(t, " seconds to execute the code")