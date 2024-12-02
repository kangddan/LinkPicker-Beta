def rootName(name: str) -> str:
    return name.rpartition('|')[-1]

    
def baseName(name: str) -> str:
    return rootName(name).rpartition(':')[-1]
    

def namespace(name: str) -> str:
    if name.find(':') != -1:
        return rootName(name).rpartition(':')[0]

    return ''
    
    
def updateNamespaceWithOptional(oldNamespaces: list, newNamespace: str) -> 'list[str]':
    updatedNamespaces = []
    for name in oldNamespaces:
        parts = name.split('|')
        updatedParts = [
            f"{newNamespace + ':' if newNamespace else ''}{part.split(':', 1)[-1]}"
            for part in parts
        ]
        updatedName = '|'.join(updatedParts)
        updatedNamespaces.append(updatedName)
    return updatedNamespaces
    
    

