from collections import defaultdict


class Node(object):
    """
        Node of a ShortestPathTree

        Properties:
        ----------
        tree: the tree to which this node belongs
        uuid: the uuid of the vertex this node represents
        children: list of children of this node
        parents: list of parents of this node
        distance: distance from s, the starting vertex
        weight: the weight of this node in calculating edge betweenness

        Methods:
        -------
        append(child): add child to this node's children, and update the trees'
            list of leaves accordingly
        connect(child_id): connect the node with id child_id to this one
    """
    def __init__(self, uuid, parents, tree):
        self.tree = tree
        self.tree.tree_dict[uuid] = self
        self.uuid = uuid
        self.children = []
        self.parents = parents
        if parents:
            self.distance = parents[0].distance + 1
            self.weight = parents[0].weight
        else:
            self.distance = 0
            self.weight = 1

    def append(self, child):
        if not self.children:
            self.tree.leaves.remove(self)
        self.children.append(child)
        self.tree.leaves.append(child)

    def connect(self, child_id):
        child = self.tree.tree_dict[child_id]
        if child.distance == self.distance + 1:
            if not self.children:
                self.tree.leaves.remove(self)
            self.children.append(child)
            child.parents.append(self)
            child.weight += self.weight

    def __str__(self):
        children = ""
        for i, child in enumerate(self.children):
            children += str(child)
            if len(self.children) > 1 + i:
                children += ", "
        string = "%s[d:%s, w:%s]" % (self.uuid, self.distance, self.weight)
        if self.children:
            string += " (%s)" % (children)
        return string


class ShortestPathTree(object):
    """
        Tree that represents the shortest path from root to every vertex
        in the graph.

        Properties:
        ----------
        tree_dict: a dict from vertex uuids to Nodes, allows for quick access
            to a node
        root: the root of the tree
        leaves: a list of the leaves of the tree
    """
    def __init__(self, start_id, graph):
        self.tree_dict = {}
        self.root = Node(start_id, [], self)
        self.leaves = [self.root]
        queue = [(start_id, self.root)]
        visited = defaultdict(bool)
        visited[start_id] = True
        while queue:
            s = queue.pop(0)
            for v in graph[s[0]]:
                if not visited[v]:
                    child = Node(v, [s[1]], self)
                    queue.append((v, child))
                    s[1].append(child)
                    visited[v] = True
                else:
                    s[1].connect(v)

    def __str__(self):
        return str(self.root)
