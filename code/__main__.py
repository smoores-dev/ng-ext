from __future__ import print_function
from data_in import read_data
from sys import argv
from dendrogram import Dendrogram
from modularity import find_best_splits

if __name__ == "__main__":
    """
        Finds the best clustering for each of the given ego network files.
        Stores output to file called submission.csv
    """
    ego_nets = read_data(argv[1])

    # Good sets (small) to test on are 25708, and 1310
    # Change this variable to change the egonet that it starts reading from
    # start = 8338
    # index = [k for k, v in tup_ls].index(start)
    index = 0  # use the line above instead if not running from start
    tup_ls = sorted(ego_nets.iteritems(), key=lambda t: t[1].size)
    out = open("submission.csv", "w")
    # out = open("out.txt", "a")  # if not running from start, use append instead
    while index < len(tup_ls):
        uid, ego_net = tup_ls[index]
        print("Analyzing ego network {0}".format(uid))
        dendrogram = Dendrogram(ego_net)
        size = ego_net.size
        best_split = find_best_splits(dendrogram.levels, size)
        circles = dendrogram.convert_to_circles()[best_split]
        circ_str = str(uid) + "," + str(len(circles)) + ","
        circ_str += ";".join([" ".join([str(fid) for fid in circle]) for circle in circles])
        print(circ_str, file=out)
        print("Best split level for ego network {0} is {1}".format(uid, best_split))
        index += 1
    out.close()
