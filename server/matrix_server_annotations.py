import numpy as np
import util_meta

# ("neuron_id", int), ("cube_id", int), ("region", int), ("cell_type", int), ("cortical_depth", int), ("cube_x", int), ("cube_y", int)]

def getAnnotationProps(props, partitions, order): 
    print("order", order)
    annotations = []
    for part in partitions:
        regionId = part[0,2]
        regionName = util_meta.getRegionDisplayName(props["regions"][regionId]["name"])
        cellTypeId = part[0,3]
        cellTypeName = props["cellTypes"][cellTypeId]["name"]
        corticalDepth = str(part[0,4])
        a = []
        if(order.index("region") < order.index("cell_type")):            
            if(order.index("cortical_depth") < order.index("region")):
                a = [corticalDepth, regionName, cellTypeName]
            elif(order.index("cortical_depth") < order.index("cell_type")):
                a = [regionName, corticalDepth, cellTypeName]
            else: 
                a = [regionName, cellTypeName, corticalDepth]
        else:
            if(order.index("cortical_depth") < order.index("cell_type")):
                a = [corticalDepth, cellTypeName, regionName]
            elif(order.index("cortical_depth") < order.index("region")):
                a = [cellTypeName, corticalDepth, regionName]
            else: 
                a = [cellTypeName, regionName, corticalDepth]
        annotations.append(a)
    return annotations