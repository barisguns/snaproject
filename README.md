# snaproject

Clustering on Social Network Graphs


By Barış Gün Sürmeli


Introduction

Clustering on social network graphs are useful to extract and explore the information about the graph such as which people are strongly connected to the other, how people are grouped between each other. This information further can be helpful for; identifying which kind of properties of the groups of people have and the properties of the people that are in this group, estimating how the propagation of information on the network would be. Thus, a distance metric between the nodes of the network is defined and a k-medoids clustering is applied on the network depending on the calculated distances.


Purpose of the Project

Purpose of the project is to identify the clusters of nodes on the social network graph by calculating the distance between all node pairs in the network.


Tools and Libraries Used

Neo4j

Python 2

R 

R package: cluster

Git

CSV

cypher


Implementation

The python script clustering1.py gets the data from neo4j database that is given for the SNA course, and tries to cluster the employees, depending "takdir" relations between employee pairs. Distance between a node-pair is defined as the reciprocal of the number of "takdir"s between them. This value is set as the weights of edges between the nodes.
For calculating the distance between two nodes that are not connected by directly an edge but there is a path between them,
the shortest path is found as the path that has lowest sum of edge weights between these nodes.
If there is no path between two nodes, then the distance is infinity ( huge value such as 1000 ).
These shortest path values are defined as the distances between all the node pairs, then the
dissimilarity matrix is constructed. This matrix is written to a CSV file which is going to be read by the R script, which implements the k-medoids algorithm for clustering.
The runtime is long due to the fetching of the data from database and the usage of the "dictionaries" which is a useful but considerably slow data structure.

The R script pam_on_graph.R  we read the CSV file that contains the dissimilarity matrix between the nodes(employees), and apply k-medoids clustering.
It randomly selects k representative nodes and then by using the distance metrics groups the dataset around them.
Then iteratively tries to detect best representative group of nodes by removing one node and adding different one randomly.
If the new group has lower clustering error, then the new group is used. 
This iterations are kept until there is no change in the representative nodes for long number of iterations.
Partitioning Around Medoids algorithm is one implementation of the k-medoids clustering and in R we have its implementation as a function: pam().
By giving the number of clusters and the dissimilarity matrix, pam() gives the names of the individuals(in our case, nodes, employee names), and which cluster they belong.


Results

Given the number of clusters, the distance metric we define works well and the resulting clusters contain the nodes that are highly connected to each other that contains many relations between them.


References

https://stat.ethz.ch/R-manual/R-devel/library/cluster/html/pam.html

https://en.wikipedia.org/wiki/Floyd–Warshall_algorithm
