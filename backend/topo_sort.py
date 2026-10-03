def topological_sort(graph):
    """
    Performs topological sorting on a directed acyclic graph.
    """

    indegree = {}

    # Calculate indegree of every applicant
    for node in graph:
        indegree[node] = 0

    for node in graph:
        for neighbour in graph[node]:
            indegree[neighbour] += 1

    # Start with applicants having no incoming edges
    queue = []

    for node in indegree:
        if indegree[node] == 0:
            queue.append(node)

    order = []

    # Process the queue
    while queue:

        node = queue.pop(0)
        order.append(node)

        for neighbour in graph[node]:

            indegree[neighbour] -= 1

            if indegree[neighbour] == 0:
                queue.append(neighbour)

    # If not all nodes were processed, a cycle exists
    if len(order) != len(graph):
        return None

    return order
