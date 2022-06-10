def getTestRequest():
    return {"configuration":
        {"orderRows": [0, 1, 2], "orderCols": [0, 1, 2], "rhoRows": 360, "rhoCols": 360, "phiRows": 0, "phiCols": 0, "selection": {"presynaptic": {}, "postsynaptic": {}}}, 
        "attributeParameters": {"rows": {"totalAtLevel": [11, 66, 396], "angleAtLevel": [32.72727272727273, 5.454545454545454, 0.9090909090909091], "numValuesAtLevel": [11, 6, 6], "colors": ["#E91E63", "#00838F", "#FF8F00"], 
            "values": [["VPM", "L2PY", "L3PY", "L4PY", "L4sp", "L4ss", "L5IT", "L5PT", "L6CC", "L6INV", "L6CT"], ["L1", "L23", "L4", "L5", "L6", "SUBCOR"], ["L1", "L2", "L3", "L4", "L5", "L6"]], 
            "attributeNames": ["cell_type", "soma_layer", "cube_layer"]}, "cols": {"totalAtLevel": [10, 50, 100], "angleAtLevel": [36, 7.2, 3.6], 
            "numValuesAtLevel": [10, 5, 2], "colors": ["#E91E63", "#303F9F", "#26C6DA"], "values": [["L2PY", "L3PY", "L4PY", "L4sp", "L4ss", "L5IT", "L5PT", "L6CC", "L6INV", "L6CT"], ["L1", "L23", "L4", "L5", "L6"], ["basal", "apical"]], "attributeNames": ["cell_type", "soma_layer", "compartment"]}
        }, 
        "tiles": {"tile_0_0": {"mode": "update", "selection": {"presynaptic": {"cell_type": "L6CT"}, "postsynaptic": {"cell_type": "L6INV"}}}}
    }
