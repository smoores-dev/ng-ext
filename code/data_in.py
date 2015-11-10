from collections import defaultdict
from graph import Graph, Vertex
from uuid import uuid4
from copy import deepcopy
import numpy as np
import os


def add_friends(graph, line):
    split_line = line.strip('\n').split(' ')
    # Find the ID of the friend in this line
    fid = int(split_line[0][:-1])
    # Generate list of friends of this friend
    ffriends = [int(f) for f in split_line[1:] if f != '']
    edges = {}
    for ffid in ffriends:
        edges[ffid] = 0
    # Store this friend's list of friends in the dict
    graph.adj_list[fid] = edges
    return len(graph.adj_list[fid].keys())


def map_graph(graph):
    """
        Create a uuid for each vertex, separate from the uid (user id).
        This allows us to split vertices later on.
    """
    id_map = {}
    for uid in graph.adj_list.keys():
        new_id = uuid4()
        id_map[uid] = new_id
        graph.vertices[new_id] = Vertex(uid, new_id)
        graph.adj_list[new_id] = deepcopy(graph.adj_list[uid])
        del graph.adj_list[uid]
    for a, edges in graph.adj_list.iteritems():
        for b in edges.keys():
            graph.adj_list[a][id_map[b]] = 0
            del graph.adj_list[a][b]


def generate_ego_nets(egonet_path):
    '''
        Reads in all ego networks

        Returns
        -------
        dictionary of IDs -> ego networks
    '''
    ego_net_lists = {}
    # Iterate through each file in directory
    for file_name in os.listdir(egonet_path):
        network_handle = open(egonet_path + file_name)
        # Find the ID for the current file
        pid = int(file_name.split('.')[0])

        graph = Graph(0)
        size = 0
        for line in network_handle:
            # Add each of the current user's friends' friendlists
            size += add_friends(graph, line)
        network_handle.close()
        map_graph(graph)
        graph.size = size / 2
        ego_net_lists[pid] = graph
    return ego_net_lists


def read_data(egonet_path):
    # First command line argument is path to egonet directory
    ego_net_lists = generate_ego_nets(egonet_path)
    print "Generated ego networks"

    return ego_net_lists
