import numpy as np

import matrix_server_filter


def getApplicableRule(props, tileKey, compatibleRules, attributeOrderRows, attributeOrderCols):
    distances = []
    for compatibleRule in compatibleRules:
        distances.append(matrix_server_filter.getDistance(tileKey, compatibleRule))    
    idx = np.argmax(distances)
    #print(">> distances", tileKey, compatibleRules, distances, idx)
    return compatibleRules[idx]    


def getCompatibleRules(tileKey, rules):
    compatible = []
    for rule in rules.keys():
        if(matrix_server_filter.areCompatible(tileKey, rule)):
            compatible.append(rule)
    return compatible


def getConstant(props, tileKey, rules, attributeOrderRows, attributeOrderCols, exactMatch):
    if(exactMatch):
        if(tileKey in rules):
            return rules[tileKey]
        else:
            return None
    else:
        compatibleRules = getCompatibleRules(tileKey, rules)        
        if(compatibleRules):
            applicableRule = getApplicableRule(props, tileKey, compatibleRules, attributeOrderRows, attributeOrderCols)
            return rules[applicableRule]
    return None



def getRulesForConnectivity(props, tileKey):
    rules = props["constants"]["bouton_weight_modified_model"]
    compatibleRules = getCompatibleRules(tileKey, rules)
    return compatibleRules


def parseRules(props, rules):
    constants = {}
    if("defaultValue" in rules):
        key = matrix_server_filter.getWildcardTileKey(props)
        constants[key] = rules["defaultValue"]
    for rule in rules["rules"]:
        selection = {
            "presynaptic" : rule["presynaptic"],
            "postsynaptic" : rule["postsynaptic"]
        }
        tileProps = {
            "selection": selection
        }
        key = matrix_server_filter.getTileKey(props, tileProps)
        constants[key] = rule["value"]
    return constants