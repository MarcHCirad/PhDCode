function createMathModel(modelType::String, param::Dict{String, Float64})
    ## Check if the math model is implemented, and if it can be created. If yes, return it.
    if modelType == "FVH"
        nbrParameters = length(fieldnames(modelFVH))
        if nbrParameters != length(param)
            println("Number of parameter is incoherent with model")
            return
        end
        myModel = modelFVH(param)
        return myModel
    elseif modelType == "RV"
        nbrParameters = length(fieldnames(modelRV))
        if nbrParameters != length(param)
            println("Number of parameter is incoherent with model")
            return
        end
        myModel = modelRV(param)
        return myModel
    elseif modelType == "EcoService"
        nbrParameters = length(fieldnames(modelEcoService))
        if nbrParameters != length(param)
            println("Number of parameter is incoherent with model EcoService")
            println("Numbers of parameters as arguments : ", length(param), " while expected number : ",
                        nbrParameters)
            println(keys(param), fieldnames(modelEcoService))
            return
        end
        myModel = modelEcoService(param)
        return myModel
    elseif modelType == "EcoServiceFV"
        nbrParameters = length(fieldnames(modelEcoServiceFV))
        if nbrParameters > length(param)
            println("Number of parameter is incoherent with model EcoServiceFV")
            println("Numbers of parameters as arguments : ", length(param), " while expected number : ",
                        nbrParameters)
            println(keys(param), fieldnames(modelEcoService))
            return
        end
        myModel = modelEcoServiceFV(param)
        return myModel
    else
        println("Model type : ", modelType, " is not implemented.")
        return
    end
end

function createNumericalModel(numericalModelType::String, mathModelType::String, 
        mathModel::mathematicalModel, numericalParam::Dict{String, Float64}, 
        initialValues::Dict{String, Float64})
    ## Check if numerical model have been implemented for math model
    ## If yes, create the numerical model
    if mathModelType == "FVH"
        if numericalModelType == "RK4"
            myModel = FVHRK4(mathModel, numericalParam, initialValues)
        elseif numericalModelType == "NSS"
            myModel = FVHNSS(mathModel, numericalParam, initialValues)
        else
            println("This type of numerical scheme is not implemented for this math. model")
        end
    elseif mathModelType == "RV"
        if numericalModelType == "RK4"
            myModel = RVRK4(mathModel, numericalParam, initialValues)
        elseif numericalModelType == "NSS"
            myModel = RVNSS(mathModel, numericalParam, initialValues)
        else
            println("This type of numerical scheme is not implemented for this math. model")
        end
    elseif mathModelType == "EcoService"
        if numericalModelType == "RK4"
            myModel = ecoServiceRK4(mathModel, numericalParam, initialValues)
        else
            println("This type of numerical scheme is not implemented for this math. model")
        end
    elseif mathModelType == "EcoServiceFV"
        if numericalModelType == "RK4"
            myModel = ecoServiceFVRK4(mathModel, numericalParam, initialValues)
        else
            println("This type of numerical scheme is not implemented for this math. model")
        end
    end
end

function readNumericalModel(dirName::String)
    fileName = dirName * "/input.txt"
    open(fileName, "r") do fin    

        readline(fin) ## Should be ## Mathematical Parameters ##

        ## Read the math model type(s)
        line = readline(fin)
        indTab = last(findfirst("    ", line))
        mathModelTypesString::String = line[last(indTab)+1:end]

        commaIndices = findall(",", mathModelTypesString)
        firstIndices = append!([1], [last(ind)+1 for ind in commaIndices])
        lastIndices = append!([first(ind)-1 for ind in commaIndices], [length(mathModelTypesString)])
        mathModelTypes = [mathModelTypesString[firstIndices[k]:lastIndices[k]] for k in 1:(length(firstIndices))]
        
        ## Read the math model parameters
        mathParam = Dict{String, Float64}()
        line = readline(fin)
        while line != "## Initial Values ##"
            indTab = findfirst("    ", line)
            mathParam[line[1:first(indTab)-1]] = tryparse(Float64, line[last(indTab)+1:end])
            line = readline(fin)
        end

        mathModels = Dict{String, T where T<:mathematicalModel}()
        for mathModelType in mathModelTypes
            myModel = createMathModel(mathModelType, mathParam)
            mathModels[mathModelType] = myModel
        end
        
        ## Read the initial values
        line = readline(fin)
        initialValues = Dict{String, Float64}()
        while line != "## Numerical Parameters ##"
            indTab = findfirst("    ", line)
            initialValues[line[1:first(indTab)-1]] = tryparse(Float64, line[last(indTab)+1:end])
            line = readline(fin)
        end
        
        ## Find the numerical model type
        line = readline(fin)
        indTab = last(findfirst("    ", line))
        numericalModelType::String = line[last(indTab)+1:end]
        numericalParam = Dict{String, Float64}()

        ## Read the numerical model parameters
        for line in eachline(fin)
            indTab = findfirst("    ", line)
            numericalParam[line[1:first(indTab)-1]] = tryparse(Float64, line[last(indTab)+1:end])
        end

        numericalModels = Dict{String, numericalModel}()
        for mathModelType in collect(keys(mathModels))
            numericalModels[mathModelType] = createNumericalModel(numericalModelType, mathModelType, 
                                                    mathModels[mathModelType], numericalParam, initialValues)
        end

        return numericalModels
    end
end
