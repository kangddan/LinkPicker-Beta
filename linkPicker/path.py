# -*- coding: utf-8 -*-


def rootName(name: str) -> str:
    """Returns the base name without group information.

    Args:
        name (str): Full path with group information.

    Returns:
        str: Name without grouping.

    Example:
        name = "base_GRP|sub_GRP|namespace:sphere_GEO"
        rootName(name) -> "namespace:sphere_GEO"
    """
    return name.rpartition('|')[-1]

    
def baseName(name: str) -> str:
    """Returns the name without groups or namespace.

    Args:
        name (str): Full path with groups and namespace.

    Returns:
        str: Name without grouping or namespace.

    Example:
        name = "base_GRP|sub_GRP|namespace:sphere_GEO"
        baseName(name) -> "sphere_GEO"
    """
    return rootName(name).rpartition(':')[-1]
    

def namespace(name: str) -> str:
    """Returns the namespace, if present.

    Args:
        name (str): Name with namespace information.

    Returns:
        str: The namespace, or None if none exists.

    Example:
        name = "namespace:base_GRP|namespace:sub_GRP|namespace:sphere_GEO"
        namespace(name) -> "namespace"
    """
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
    
    

