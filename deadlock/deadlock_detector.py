class DeadlockDetector:
    def __init__(self):
        self.graph = None

    def detect_cycle(self, graph):
        state = {
            node: 0
            for node in graph
        }
        path = []

        for node in graph:
            if state[node] == 0:
                cycle = self._dfs(node, graph, state, path)

                if cycle is not None:
                    return cycle
        return None

    def _dfs(self, node, graph, state, path):
        state[node] = 1
        path.append(node)

        for neighbor in graph.get(node, set()):
            if state[neighbor] == 1:
                cycle_start = path.index(neighbor)
                return path[cycle_start:]

            if state[neighbor] == 0:
                cycle = self._dfs(neighbor, graph, state, path)

                if cycle is not None:
                    return cycle

        state[node] = 2
        path.pop()
        return None