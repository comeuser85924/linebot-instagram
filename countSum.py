def handleCount(dataList):
    if('edge_sidecar_to_children' in dataList):
        return len(dataList['edge_sidecar_to_children']['edges'])
    return 1