from __future__ import division
from collections import defaultdict
from data_in import read_data
from sys import argv
from operator import itemgetter
from graph import Vertex
from shortest_path_tree import ShortestPathTree
from itertools import combinations
from copy import copy


class Node(object):
    """
        Node of a Dendrogram

        Properties:
        ----------
        graph: connected component of the original graph
        clone: clone of self.graph. Allows us to remove edges without
            messing with the graph
        parent: reference to parent node
        left, right: reference to children nodes. If None, then self
            is a leaf. If only self.right is None, graph is a singleton node
        edge_comparisons: dictionary that maps from a node id to many edges
            were removed to split this node and that one
        level: the level of this node in the dendrogram

        Methods:
        -------
        calculate_e_betweenness(): recalculate edge betweenness. Uses the clone,
            NOT the graph. Call after removing an edge
        calculate_v_betweenness(): recalculate vertex betweenness using edge
            betweenness. Call after calculating edge betweenness
    """
    def __init__(self, tree, graph, parent):
        self.tree = tree
        self.id = self.tree.node_cnt
        self.graph = graph
        self.clone = self.graph.clone()
        self.parent = parent
        self.level = parent.level + 1 if parent else 0
        self.tree.levels[self.level].append(self)
        self.removed_edges = 0
        self.edge_comparisons = defaultdict(int)
        self._left = None
        self._right = None
        self.calculate_e_betweenness()
        self.tree.node_cnt += 1

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, graph):
        self._left = Node(self.tree, graph, self)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, graph):
        self._right = Node(self.tree, graph, self)

    def set_edge_comparisons(self):
        for node in self.tree.levels[self.level - 1]:
            if node != self.parent:
                self.edge_comparisons[node.left.id] = self.parent.edge_comparisons[node.id]
                if node.right:
                    self.edge_comparisons[node.right.id] = self.parent.edge_comparisons[node.id]

    def calculate_e_betweenness(self):
        if self.clone.size > 0:
            self.clone.sp_trees = []
            self.clone.reset_betweenness()
            for vertex in self.clone.adj_list.keys():
                score_list = defaultdict(lambda: defaultdict(int))
                # Calculate the distance and weights
                cur_sp_tree = ShortestPathTree(vertex, self.clone.adj_list)
                self.clone.sp_trees.append(cur_sp_tree)
                queue = []
                visited = defaultdict(bool)
                for leaf in cur_sp_tree.leaves:
                    visited[leaf.uuid] = defaultdict(bool)
                    for node in leaf.parents:
                        visited[leaf.uuid][node.uuid] = True
                        if node not in queue:
                            queue.append(node)
                        score = node.weight / leaf.weight
                        score_list[leaf.uuid][node.uuid] = score
                        score_list[node.uuid][leaf.uuid] = score
                while queue:
                    child = queue.pop(0)
                    visited[child.uuid] = defaultdict(bool)
                    for parent in child.parents:
                        if not visited[child.uuid][parent.uuid]:
                            score = 0
                            for c in child.children:
                                edge = score_list[c.uuid][child.uuid]
                                score += edge
                            score += 1
                            score *= (parent.weight / child.weight)
                            score_list[child.uuid][parent.uuid] = score
                            score_list[parent.uuid][child.uuid] = score
                            if parent not in queue:
                                queue.append(parent)
                            visited[child.uuid][parent.uuid] = True
                for a, edge_list in score_list.iteritems():
                    for b, score in edge_list.iteritems():
                        self.clone.adj_list[a][b] += score
            self.clone.set_max_edge()

    def calculate_v_betweenness(self):
        n = len(self.clone.adj_list.keys())  # number of vertices in the graph
        best_edge_score = self.tree.best_edge(self.level)[3]
        for uuid, edges in self.clone.adj_list.iteritems():
            score = sum([b - (n - 1) for b in edges.values()]) / 2
            vertex = self.clone.vertices[uuid]
            vertex.v_betweenness = score
            vertex.reset()
            if score > best_edge_score:
                self.clone.viable_vertices.append(vertex)


class Dendrogram(object):
    """
        Dendrogram representing each level of splitting in a graph

        Properties:
        ----------
        levels: dictionary, maps integers (0 - num_levels) to a list of nodes
            on that level of the dendrogram
        root: the root node of the dendrogram

        Methods:
        -------
        convert_to_circles(): return a dict, maps ints (0 - num_levels) to a
            list of circles, where each circle is a list of graph vertices
    """
    def __init__(self, network):

        print "\tCreating dendrogram..."

        self.levels = defaultdict(list)
        self.node_cnt = 0
        self.root = Node(self, network, None)
        self.initial_split(network)

        level = 1
        removed_edges = 0

        while removed_edges < network.size:
            is_connected = True
            while is_connected:
                splittable_vertices = self.splittable_vertices(level)
                best_vertex = (None, None, None, None, 0)
                best_node, i, j, e_score = self.best_edge(level)
                for v in splittable_vertices:  # calculate split betweennesses
                    node = v[0]
                    vertex = v[1]
                    node.clone.set_pair_betweenness(vertex)
                    if vertex.pair_betweennesses.keys():
                        vertex.set_split_betweenness()
                        if vertex.split_betweenness[2] > best_vertex[4]:
                            best_vertex = (node, vertex) + vertex.split_betweenness
                if best_vertex[4] > e_score:  # should split vertex instead of remove edge
                    best_node, vertex, side_one, side_two, v_score = best_vertex
                    j = best_node.clone.split_vertex(vertex, side_one, side_two)
                    i = vertex.uuid
                else:  # remove edge as usual
                    best_node.clone.remove_edge(i, j, best_node)
                    removed_edges += 1
                best_node.calculate_e_betweenness()
                is_connected, children = best_node.clone.connected_components(i, j)
            best_node.left, best_node.right = children
            best_node.left.edge_comparisons[best_node.right.id] = best_node.removed_edges
            best_node.right.edge_comparisons[best_node.left.id] = best_node.removed_edges
            for node in self.levels[level]:
                if node != best_node:
                    node.left = node.clone  # propogate everything to the next level
                node.set_edge_comparisons()
            level += 1

    def initial_split(self, network):
        """
            Put each connected component of the initial graph into its own node
        """
        is_connected = True
        pairs = list(combinations(network.adj_list.keys(), 2))
        while is_connected and pairs:
            i, j = pairs.pop()
            is_connected, children = network.connected_components(i, j)
            if not is_connected:
                left, right = children
                Node(self, left, self.root)
                self.initial_split(right)
                return
        Node(self, network, self.root)

    def best_edge(self, level):
        """
            Parameters:
            ----------
            level: level of dendrogram to find best edge for

            Returns:
            -------
            (node, i, j, betweenness) where node is the node containing edge {i, j}
                and {i, j} is the edge with highest betweenness in nodes
        """
        bests = []
        for node in self.levels[level]:
            if node.clone.size > 0:
                bests.append((node,) + node.clone.max_e_betweenness)
        return max(bests, key=itemgetter(2))

    def splittable_vertices(self, level):
        """
            Parameters:
            ----------
            level: level of dendrogram to find splittable vertices for

            Returns:
            -------
            (node, vertex) where node is the node containing vertex v
                and v has vertex betweenness greater than the max edge
                betweenness
        """
        bests = []
        for node in self.levels[level]:
            node.calculate_v_betweenness()
            if node.clone.viable_vertices:
                for v in node.clone.viable_vertices:
                    bests.append((node, v))
                node.clone.viable_vertices = []
        return bests

    def convert_to_circles(self):
        """
            Returns:
            -------
            A dict mapping ints (levels) to a list of circles at that level of
                splitting
        """
        out = {}
        for k, v in self.levels.iteritems():
            out[k] = [[n.graph.vertices[uid].uid for uid in n.graph.adj_list.keys()] for n in v]
        return out

    def __str__(self):
        return str(self.convert_to_circles())

if __name__ == "__main__":
    ego_net_lists, features, circles = read_data(*argv[1:])
    dendrogram = Dendrogram(ego_net_lists[1310])
