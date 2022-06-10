
def computeTilingPattern(props, configuration):
    meta = props["meta"]
    patterns = {}
    rowAttributes = meta["rows"]["attributes"]
    colAttributes = meta["cols"]["attributes"]
    rowOrder = configuration["orderRows"]
    colOrder = configuration["orderCols"]
    for i in range(0, len(rowAttributes)):
        for j in range(0, len(colAttributes)):
            rowAttribute = rowAttributes[rowOrder[i]]
            colAttribute = colAttributes[colOrder[j]]
            rowValues = rowAttribute["values"]
            colValues = colAttribute["values"]
            nRowTiles = len(rowValues)
            nColTiles = len(colValues)
            pattern = {}
            pattern["nRows"] = nRowTiles
            pattern["nCols"] = nColTiles
            pattern["rowAnnotations"] = rowValues
            pattern["colAnnotations"] = colValues
            pattern["rowColor"] = rowAttribute["color"]
            pattern["colColor"] = colAttribute["color"]
            patterns["{}_{}".format(i, j)] = pattern
    return patterns
