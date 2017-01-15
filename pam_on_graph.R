# In this script, we read the CSV file that contains the dissimilarity matrix between the nodes(employees), and apply k-medoids clustering.
# It randomly selects k representative nodes and then by using the distance metrics groups the dataset around them.
# Then iteratively tries to detect best representative group of nodes by removing one node and adding different one randomly.
# If the new group has lower clustering error, then the new group is used. 
# This iterations are kept until there is no change in the representative nodes for long number of iterations.
# Partitioning Around Medoids algorithm is one implementation of the k-medoids clustering and in R we have its implementation as a function: pam().
# By giving the number of clusters and the dissimilarity matrix, pam() gives the names of the individuals(in our case, nodes, employee names), and
# which cluster they belong.

require(cluster) # This package has to be installed in order to use the function pam(). 
dissimilaritymatrix = read.csv(file="ttest.csv",head=TRUE, sep = "") # reads the dissimilarity matrix from the CSV file
# THE PATH OF THE CSV FILE HAS TO BE GIVEN IN THE ABOVE LINE
# OTHERWISE, YOU CAN PUT THE CSV FILE INTO YOUR WORKING DIRECTORY
# to learn your working directory, use: print(getwd())

# CODE SNIPPET 1: This code snippet is written for calculating the best K value.
# IF we start clustring with k = 1 and then increase, the best number of clusters is expected at the point where; 
# when the k number is increased, there is no significant decrease in the clustering error.
# one idea to define "significant" I tried to detect the point where the error has the biggest decrease. This does not seem to work well, 
# so, so far, I give the k value by hand and check if there are significant clustering.
kmax = length(dissimilaritymatrix)-1

errorfor_k = vector(mode = "numeric", length = kmax)
ks = vector(mode = "character", length = kmax)

for (k in 1:kmax){
  cls = pam(as.dist(dissimilaritymatrix), k, TRUE)
  errorfor_k[k] <- as.numeric(cls$objective)/100
  ks[k] <- as.character(k)
}

maxdif = 0
bestk = 0

for (k in (1):(kmax-1)){
  ks = errorfor_k[k]
  kf = errorfor_k[k+1]
  if  (ks-kf > maxdif){
    maxdif <- ks-kf
    bestk <- k+1
  }
}
# CODE SNIPPET 1: END

k = 50

cls = pam(as.dist(dissimilaritymatrix), k, TRUE)
print("clustering results: ")
# Given k = 50, we see that clustering is reasonable. If we check the neo4j graph for k value 50, we see that the groups of nodes that gave "takdir"s to
# each other are in the same cluster, the nodes that do not have any path to another are all has their own cluster.
print(cls$clustering)


