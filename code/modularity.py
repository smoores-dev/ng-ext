from __future__ import division
from scipy.signal import argrelmax
from operator import itemgetter
import itertools
import numpy as np


def find_best_splits(dendrogram, num_total_edges):
    '''
        Given a specific level of division of our hierarchy, this function will
        calculate the e-matrix (defined below).

        Parameters:
        -----------
        dendrogram: the specific hierarchy for which we are calculating the
            e-matrix.

            A circles is represented as follows:
                - A circle is a list of user IDs, associated with that
                    community.
                - Circles is a list of circles, which represents one level of
                    the dendrogram.

        num_total_edges: the total number of edges in the original network.


        Returns:
        --------
        The split level that provides the best clustering

    '''
    print "\tComputing modularity..."
    qs = np.ndarray(len(dendrogram.values()))
    for n, level in enumerate(dendrogram.values()):
        k = len(level)
        # Create an empty e matrix.
        e = np.zeros(shape=(k, k), dtype=float)
        # Create all pairs of combinations of circles. Since our matrix is symmetric this saves us some time.
        circleIDs = range(k)
        all_pairs = itertools.combinations(circleIDs, 2)
        for (i, j) in all_pairs:
            node_i = level[i]
            node_j = level[j]
            # print "Comparing circle %s and circle %s" % (node_i, node_j)
            removed_edges = node_i.edge_comparisons[node_j.id]
            e[i][j] = removed_edges/num_total_edges
            e[j][i] = removed_edges/num_total_edges
        for m in xrange(k):
            e[m][m] = (level[m].graph.size)/num_total_edges
        qs[n] = calc_modularity(e)
    return sort_max(qs)[0]


def sort_max(qs):
    """
        Identify the relative maxima in qs, and return them sorted from best
        to worst
    """
    sorted_maxes = sorted([(i, qs[i]) for i in list(argrelmax(qs)[0])],
                          key=itemgetter(1), reverse=True)
    return [x for x, y in sorted_maxes]


def calc_modularity(e):
    '''
        Implements the modularity measure, as specified on p8. of the paper.
    '''
    q = np.trace(e) - np.sum(np.square(e))
    return q
