from collections import defaultdict, Iterable
from copy import deepcopy
from operator import itemgetter
from uuid import uuid4
import itertools


def flatten(tup):
    for el in tup:
        if isinstance(el, Iterable):
            for sub in flatten(el):
                yield sub
        else:
            yield el


class Vertex(object):
    """Vertex of a Graph"""
    def __init__(self, uid, uuid):
        self.uuid = uuid
        self.uid = uid
        self.v_betweenness = None
        self.pair_betweennesses = defaultdict(lambda: defaultdict(int))
        self.split_betweenness = None

    def find_min_pair(self):
        best = (None, None, float('inf'))
        for a, edges in self.pair_betweennesses.iteritems():
            for b, score in edges.iteritems():
                if score < best[2]:
                    best = (a, b, score)
        return best[0], best[1]

    def coalesce(self):
        i, j = self.find_min_pair()
        coalesce = tuple(flatten((i, j)))
        for k in self.pair_betweennesses.keys():
            if k != i and k != j:
                i_score = self.pair_betweennesses[i][k]
                j_score = self.pair_betweennesses[j][k]
                self.pair_betweennesses[coalesce][k] = i_score + j_score
                self.pair_betweennesses[k][coalesce] = i_score + j_score
                del self.pair_betweennesses[k][i]
                del self.pair_betweennesses[k][j]
        del self.pair_betweennesses[i]
        del self.pair_betweennesses[j]

    def set_split_betweenness(self):
        while len(self.pair_betweennesses.keys()) > 2:
            self.coalesce()
        uids = self.pair_betweennesses.keys()
        score = self.pair_betweennesses[uids[0]][uids[1]]
        self.split_betweenness = (uids[0], uids[1], score)

    def reset(self):
        self.pair_betweennesses = defaultdict(lambda: defaultdict(int))
        self.split_betweenness = None


class Graph(object):
    """Wrapper class for a graph"""
    def __init__(self, size):
        self.size = size
        self.adj_list = {}
        self.vertices = {}
        self.viable_vertices = []
        self.sp_trees = []
        self.max_e_betweenness = None
        self.max_v_betweenness = None

    def reset_betweenness(self):
        for a, edge_list in self.adj_list.iteritems():
            for b, score in edge_list.iteritems():
                self.adj_list[a][b] = 0

    def set_max_edge(self):
        """
            Parameters:
            ----------
            score_list: adjacency list style dictionary that maps to betweenness
            scores

            Returns:
            -------
            (i, j, betweenness)
        """
        ig1 = itemgetter(1)
        ig2 = lambda t: t[1][1]
        max_edge = max([(uid, max(edges.iteritems(), key=ig1)) for uid, edges in self.adj_list.iteritems() if edges], key=ig2)
        self.max_e_betweenness = max_edge[0], max_edge[1][0], max_edge[1][1]

    def clone(self):
        graph = Graph(self.size)
        graph.adj_list = deepcopy(self.adj_list)
        graph.vertices = deepcopy(self.vertices)
        return graph

    def set_pair_betweenness(self, vertex):
        for sp_tree in self.sp_trees:
            parents = sp_tree.tree_dict[vertex.uuid].parents
            children = sp_tree.tree_dict[vertex.uuid].children
            for j in children:
                for k in parents:
                    vertex.pair_betweennesses[j.uuid][k.uuid] += 1
                    vertex.pair_betweennesses[k.uuid][j.uuid] += 1
        uids = vertex.pair_betweennesses.keys()
        for i, j in itertools.combinations(uids, 2):
            if j not in vertex.pair_betweennesses[i].keys():
                vertex.pair_betweennesses[i][j] = 0
                vertex.pair_betweennesses[j][i] = 0

    def remove_edge(self, i, j, node):
        del self.adj_list[i][j]
        del self.adj_list[j][i]
        self.size -= 1
        node.removed_edges += 1

    def split_graph(self, first_component):
        """
            Parameters:
            ----------
            first_component: list of vertices in the first of two components
                that the graph will be split into

            Returns:
            -------
            left_list, right_list: each is an adjacency list representing
                one connected component of the original graph
        """
        left = Graph(0)
        right = Graph(0)
        for k, v in self.adj_list.iteritems():
            old_vert = self.vertices[k]
            if k in first_component:
                left.adj_list[k] = deepcopy(v)
                left.vertices[k] = Vertex(old_vert.uid, k)
                left.size += len(left.adj_list[k])
            else:
                right.adj_list[k] = deepcopy(v)
                right.vertices[k] = Vertex(old_vert.uid, k)
                right.size += len(right.adj_list[k])
        right.size, left.size = (right.size / 2, left.size / 2)
        return left, right

    def connected_components(self, i, j):
        '''
            Parameters
            ----------
            i, j: two mapped vertices to test connection between

            Returns
            -------
            (is_connected : boolean) - whether there's a path connecting i to j
            (components : (list[IDs], list[IDs])) - if there's no path, returns the
            two connected components
        '''
        queue = [i]
        visited = defaultdict(bool)
        visited[i] = True
        while queue:
            s = queue.pop(0)
            for child in self.adj_list[s]:
                if not visited[child]:
                    if child == j:
                        return True, []
                    visited[child] = True
                    queue.append(child)
        return False, self.split_graph(visited.keys())

    def split_vertex(self, vertex, side_one, side_two):
        """
            Parameters:
            ----------
            vertex: the vertex to be split
            side_one, side_two: the edges to be placed on each vertex after
                the split

            Returns:
            -------
            new_id: the new vertex's ID
        """
        new_id = uuid4()
        new_vertex = Vertex(vertex.uid, new_id)
        self.vertices[new_id] = new_vertex
        self.adj_list[new_id] = {}
        if isinstance(side_one, Iterable):
            for v in side_one:
                del self.adj_list[v][vertex.uuid]
                del self.adj_list[vertex.uuid][v]
                self.adj_list[v][new_id] = 0
                self.adj_list[new_id][v] = 0
        else:
            del self.adj_list[side_one][vertex.uuid]
            del self.adj_list[vertex.uuid][side_one]
            self.adj_list[side_one][new_id] = 0
            self.adj_list[new_id][side_one] = 0
        return new_id
