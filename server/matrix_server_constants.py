def getOrdersRBCCellular():
    return [
        ["region", "cell_type", "septum", "cortical_depth", "soma_x", "soma_y", "soma_z"],
        ["cell_type", "region", "septum", "cortical_depth", "soma_x", "soma_y", "soma_z"],
        ["cortical_depth", "cell_type", "region", "septum", "soma_x", "soma_y", "soma_z"],
        ["cortical_depth", "region", "cell_type", "septum", "soma_x", "soma_y", "soma_z"],
        ["soma_x", "soma_y", "soma_z", "region", "cell_type", "septum", "cortical_depth"],
        ["soma_y", "soma_x", "soma_z", "region", "cell_type", "septum", "cortical_depth"],
        ["soma_z", "soma_x", "soma_y", "region", "cell_type", "septum", "cortical_depth"]
    ]

def getOrdersCompareInference():
    return [
        ["cell_type", "region", "neuron_id", "cube_id", "cortical_depth", "cube_x", "cube_y"]
    ]

def getOrders(datasetName):
    if(datasetName == "comparisonInference"):
        return [
            ["region", "cell_type", "cortical_depth", "neuron_id", "cube_id", "cube_x", "cube_y"],
            ["cell_type", "region", "cortical_depth", "neuron_id", "cube_id", "cube_x", "cube_y"],
            ["cortical_depth", "region", "cell_type", "neuron_id", "cube_id", "cube_x", "cube_y"],
            ["cortical_depth", "cube_x", "cube_y", "region", "cell_type", "neuron_id", "cube_id"],
            ["cube_x", "region", "cell_type", "cortical_depth", "cube_y", "neuron_id", "cube_id"],
            ["neuron_id", "region", "cell_type", "cortical_depth", "cube_x", "cube_y", "cube_id"]
        ]
    elif(datasetName == "RBCCellular"):
        return [
            ["region", "cell_type", "septum", "cortical_depth", "soma_x", "soma_y", "soma_z"],
            ["cell_type", "region", "septum", "cortical_depth", "soma_x", "soma_y", "soma_z"],
            ["cortical_depth", "cell_type", "region", "septum", "soma_x", "soma_y", "soma_z"],
            ["cortical_depth", "region", "cell_type", "septum", "soma_x", "soma_y", "soma_z"],
            ["soma_x", "soma_y", "soma_z", "region", "cell_type", "septum", "cortical_depth"],
            ["soma_y", "soma_x", "soma_z", "region", "cell_type", "septum", "cortical_depth"],
            ["soma_z", "soma_x", "soma_y", "region", "cell_type", "septum", "cortical_depth"]
        ]
    else:
        raise RuntimeError("invalid dataset name: {}".format(datasetName))



def getDefaultOrder(datasetName):
    return getOrders(datasetName)[0]