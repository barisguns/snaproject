# This script gets the data from neo4j database that is given for the SNA course, and tries to cluster the employees,
# depending "takdir" relations between employee pairs.
# distance between a node-pair is defined as the reciprocal of the number of "takdir"s between them.
# this value is set as the weights of edges between the nodes.
# for calculating the distance between two nodes that are not connected by directly an edge but there is a path between them,
# the shortest path is found as the path that has lowest sum of edge weights between these nodes.
# if there is no path between two nodes, then the distance is infinity ( huge value such as 1000 ).
# these shortest path values are defined as the distances between all the node pairs, then the
# dissimilarity matrix is constructed. This matrix is written to a CSV file which is going to be read by the R script,
# which implements the k-medoids algorithm for clustering.
# the runtime is long due to the fetching of the data from database and the usage of the "dictionaries" which is a
# useful but considerably slow data structure.

from neo4jrestclient.client import GraphDatabase
import csv
import random
# Create some nodes with labels
from neo4jrestclient import client


def dissfromdic(dic, row):
    # given the dictionary that holds the distances between node couples and a row that contains all the nodes,
    # this function creates the dissimilarity matrix for the nodes and then writes it to a "csv"(comma seperated values)
    # file. The first row of the matrix contains will contain the names of the nodes (header of the csv file).
    matchingres = dic
    files = row

    distmat = []
    for i in range(len(files)):
        distmat.append([])
        for j in range(len(files)):
            distmat[i].append(0)

    # print files

    for i in range(len(files)):
        a = files[i]
        for j in range(len(files)):
            b = files[j]
            if a != b:
                if (a, b) in matchingres.keys():
                    distmat[i][j] = matchingres[(a, b)]
                else:
                    distmat[i][j] = matchingres[(b, a)]
            else:
                distmat[i][j] = 0

    # write the dissimilarty matrix with the header to the CSV file.
    distmat.append([])
    k = len(files)
    for l in range(len(files)):
        distmat[k] = distmat[k-1]
        k -= 1
    distmat[0] = files

    ofile = open('ttest.csv', "wb")
    writer = csv.writer(ofile, delimiter='	', quotechar='"', quoting=csv.QUOTE_ALL)

    for name in range(len(distmat[0])):
        distmat[0][name] = distmat[0][name].encode('utf-8')

    for row in distmat:
        writer.writerow(row)

    ofile.close()
    # write the dissimilarty matrix with the header to the CSV file. ENDS


db = GraphDatabase("http://localhost:7474", username="neo4j", password="123456") # establish connection with the db

q1 = 'MATCH (n:Employee)-[t_aldi:TAKDIR_ALDI]->(p:Takdir)<-[t_etti:TAKDIR_ETTI]-(m:Employee) RETURN n, m'
# get all the pairs of employees that has a takdir relation between each other. This includes some pairs multiple times,
#  this will be handled later

results1 = db.query(q1, returns=(client.Node, client.Node))

q1 = 'MATCH (n:Employee) Return n'
results2 = db.query(q1, returns=client.Node)
# get all the employee nodes

dist = {}  # the dictionary that will hold the distances between the employee node pairs


# Floyd-Warshall Algorithm - Finding shortest paths between edges

# To approximate the tie strength (edge weights) we divide 1 by the num of "takdir"s for each edge
# so our edge weight formula is: weight = 1/number of "takdir"s
for i in results2:
    for j in results2:
        tup = (i[0]["name"], j[0]["name"])
        # print tup
        if i == j:
            dist[tup] = 0
        else:
            dist[tup] = 10
# with the above piece of code we have 0 distance between the node pairs such as (x,x) (same node)
# and we have value 1000 (big value) distance between the nodes that has no relation between them

nodes = []  # will hold the names of the employees
for i in results2:
    nodes.append(i[0]["name"])

for i in results1:
    # here we create the "weighted adjacency matrix" and also handle the redundant node pairs;
    # for each node pair, the number of "takdir"s between them is equal to the weight of the edge between them
    # actually, we do not create a matrix but we imitate it with a dictionary such as dict[node-pairs] = edge weight value
    tup1 = (i[0]["name"], i[1]["name"])
    tup2 = (i[1]["name"], i[0]["name"])
    if dist[tup1] == 1000:
        dist[tup1] = 1
    elif dist[tup1] is not 0:
        dist[tup1] += 1

    if dist[tup2] == 1000:
        dist[tup2] = 1
    elif dist[tup2] is not 0:
        dist[tup2] += 1

# since we consider tie-strength as inverse of the number of "takdir"s,
#  we change the edge weight values with their reciprocals
for i in dist:
    if dist[i] is not 0 and dist[i] is not 1000:
        dist[i] = float(1/float(dist[i]))

# core of the floyd-warshall algorihm; given the weighted adjacency matrixes, where higher weight means more distance
# between pairs, the "dissimilarity matrix" is found where the distances are the shortest paths that are calculated
# where the edge weights are the distances between pairs.
# for each node, at each iteration, neighborhood is expanded and checked if there is a shorter path between the
# corresponding node and the other nodes. If there is, the shortest path is updated
for k in nodes:
    for i in nodes:
        for j in nodes:
            if dist[(i, j)] > dist[(i, k)] + dist[(k, j)]:
                dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
# Floyd-Warshall Algorithm ENDS

dissfromdic(dist, nodes)

# BELOW CODE is my implementation of the k-medoids algoritm. Even it works well, it has lower performance than the
# implementation in R-language. So I use the functions in R.

#
# def calc_abserr(clstrs, meds):
#     abs_er = 0
#     for a in clstrs:
#         clstind = clstrs.index(a)
#         for b in a:
#             abs_er += dist[(b, meds[clstind])]
#     return abs_er

# # A k-Medoids algorithm: PAM
# k = 50
#
# # arbitrarily choose k objects in D as the initial representative objects or seeds
# # "Reservoir Sampling" for choosing k elements randomly
#
# medoids = []
#
# for i, smp in enumerate(nodes):
#     if i < k:
#         medoids.append(smp)
#     elif i >= k and random.random() < k / float(i + 1):
#         replace = random.randint(0, len(medoids) - 1)
#         medoids[replace] = smp
#
# # Reservoir Sampling END
#
# clusters = []
# for i in medoids:
#     lst = [i]
#     clusters.append(lst)
#
# # assign each remaining object to the cluster with the nearest representative object
# for i in nodes:
#     mindist = 1000
#     closest = medoids[0]
#     already = False
#     for j in medoids:
#         if i not in medoids:
#             d = dist[(i, j)]
#             if d <= mindist:
#                 mindist = d
#                 closest = j
#         else:
#             already = True
#
#     if already is not True:
#         ind = medoids.index(closest)
#         clusters[ind].append(i)
#
# # compute the absolute error of the clustering
# abs_err = calc_abserr(clusters, medoids)
#
# iters = 0
# while 1:
#     old_medoids = medoids[:]
#     clusters = []
#     # randomly select a nonrepresentative object
#     while 1:
#         rand = random.choice(nodes)
#         if rand not in medoids:
#             break
#
#     current_med = random.choice(medoids)
#     ind = medoids.index(current_med)
#     new_medoids = medoids[:]
#     new_medoids[ind] = rand
#
#     for i in new_medoids:
#         lst = [i]
#         clusters.append(lst)
#
#     # assign each remaining object to the cluster with the nearest representative object
#     for i in nodes:
#         mindist = 1000
#         closest = new_medoids[0]
#         if i not in new_medoids:
#             for j in new_medoids:
#                 d = dist[(i, j)]
#                 if d <= mindist:
#                     mindist = d
#                     closest = j
#
#             ind = new_medoids.index(closest)
#             clusters[ind].append(i)
#
#     # compute the absolute error of the clustering
#     new_abs_err = calc_abserr(clusters, new_medoids)
#
#     x = abs(new_abs_err - abs_err)
#     # print x
#     if x == 0 and iters >= 300:
#         break
#
#     if new_abs_err < abs_err:
#         medoids = new_medoids[:]
#         abs_err = new_abs_err
#
#     iters += 1
#
# max = 0
# for i in clusters:
#     if len(i) > max:
#         max = len(i)
#     print i
#
# print max
#

