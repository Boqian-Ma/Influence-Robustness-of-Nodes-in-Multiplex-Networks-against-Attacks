from collections import defaultdict
from array import array

from subroutines.core import core
from subroutines.commons import *
from utilities.time_measure import ExecutionTime

import os
from operator import itemgetter, mul

import json

def breadth_first(multilayer_graph, print_file, distinct_flag):
    # measures
    number_of_cores = 0
    number_of_computed_cores = 0

    # start of the algorithm
    execution_time = ExecutionTime()

    # create the vector of zeros from which start the computation
    start_vector = tuple([0] * multilayer_graph.number_of_layers)

    # dict of cores
    cores = {}

    # core [0]
    if print_file is not None and not distinct_flag:
        print_file.print_core(start_vector, array('i', multilayer_graph.get_nodes()))
    elif distinct_flag:
        cores[start_vector] = array('i', multilayer_graph.get_nodes())
    number_of_cores += 1

    # initialize the queue of vectors with the descendants of start_vector and the structure that for each vector saves its ancestor vectors
    vectors_queue = deque()
    ancestors = {}
    for index in multilayer_graph.layers_iterator:
        # start from root, find first children
        descendant_vector = build_descendant_vector(start_vector, index)
        # Add to queue
        vectors_queue.append(descendant_vector)
        # map to father set
        ancestors[descendant_vector] = [start_vector]

    print(ancestors)

    # initialize the dictionary that for each vector counts the number of descendants in the queue
    descendants_count = defaultdict(int)

    # while vectors_queue is not empty

    # find influence of all nodes on level 1

    

    # Initialise influence dict
    influence = {}

    print "initial nodes: " 
    for node in multilayer_graph.get_nodes():
        # print(str(node))
        influence[node] = 1
    print(influence)

    level = 1

    weight = {}
    # Influence ranking by level in lattice and by node
    inf_by_core_vector = {}
    # initialise inf_by_core_vector

    while len(vectors_queue) > 0:
        # remove a vector from vectors_queue (FIFO policy BFS)
        vector = vectors_queue.popleft()
        
        # if the number of non zero indexes of vector is equal to the number of its ancestors, build the intersection of its ancestor cores
        
        # if the number 
        number_of_non_zero_indexes = len([index for index in vector if index > 0])
        number_of_ancestors = len(ancestors[vector])

        if number_of_non_zero_indexes == number_of_ancestors:
            
        
            if sum(list(vector)) > level:   # whenever we go down a level in the core lattice
                # count how many times a node appeared in the level above
                influence = get_influence_v1(influence, multilayer_graph, level, cores)
                level += 1


            ancestors_intersection = build_ancestors_intersection(ancestors[vector], cores, descendants_count, distinct_flag, multilayer_graph=multilayer_graph)

            # if the intersection of its ancestor cores is not empty
            if len(ancestors_intersection) > 0:
                # compute the core from it
                k_core = core(multilayer_graph, vector, ancestors_intersection)
                number_of_computed_cores += 1
            # otherwise
            else:
                # delete its entry from ancestors and continue
                del ancestors[vector]
                continue

            # if the core is not empty
            if len(k_core) > 0:
                # add the core to the dict of cores and increment the number of cores
                cores[vector] = k_core

                number_of_cores += 1
                if print_file is not None and not distinct_flag:
                    print_file.print_core(vector, k_core)

                # compute its descendant vectors by plusing 1 on each element
                for index in multilayer_graph.layers_iterator:
                    descendant_vector = build_descendant_vector(vector, index)

                    try:
                        # update the list of the ancestors of the descendant vector
                        ancestors[descendant_vector].append(vector)

                    # if the descendant vector has not already been found
                    except KeyError:
                        # add the descendant vector to the queue
                        vectors_queue.append(descendant_vector)
                        ancestors[descendant_vector] = [vector]

                    # increment descendants_count
                    descendants_count[vector] += 1
                    # print("descendents_count: " + str(descendants_count))
        else:
            # for each ancestor of vector
            for ancestor in ancestors[vector]:
                # decrement its number of descendants
                decrement_descendants_count(ancestor, cores, descendants_count, distinct_flag)

        # delete vector's entry from ancestors after finding the core
        # only keep those directly above
        del ancestors[vector]
    # end of the algorithm
    execution_time.end_algorithm()
    print("influence: " + str(influence))

    print_influence(influence, "/Users/adamma/Desktop/research/multilayer_core_decomposition/output")

    # print algorithm's results
    print_end_algorithm(execution_time.execution_time_seconds, number_of_cores, number_of_computed_cores)
    # execute the post processing
    post_processing(cores, distinct_flag, print_file)

    print(weight)
    print(inf_by_core_vector)




def print_influence(influence, path):
    sort_influence = sorted(influence.items(), key = itemgetter(1), reverse=True)
    with open(os.path.join(path, "influence_v1.txt"), 'w+') as f:
        for i in sort_influence:
            f.write(str(i[0]) + "\t" + str(i[1]) + "\n")

def get_influence_v1(influence, multilayer_graph, level, cores):

    '''
    eq.1 in resiliance against network attack
    '''

    count = {}                  # Count how many times a node appeared in the level

    print ("core items : " + str(cores.items()))

    for v, c in cores.items():  
        for n in multilayer_graph.get_nodes():
            if n in c:
                if n not in count:
                    count[n] = 1
                else:
                    count[n] += 1

    for v, c in influence.items():
        if v in count:
            # update
            influence[v] = count[v] * level * influence[v]
    
    return influence

def get_influence_v2(influence, multilayer_graph, level, cores):

    '''
    eq.1 in resiliance against network attack
    '''
    count = {}                  # Count how many times a node appeared in the level

    for v, c in cores.items():  
        for n in multilayer_graph.get_nodes():
            if n in c:
                if n not in count:
                    count[n] = 1
                else:
                    count[n] += 1

    for v, c in influence.items():
        if v in count:
            # update
            influence[v] = count[v] * level * influence[v] # multiple by the number of nodes in the core correspond to v
    
    return influence


def count_node_apprence_in_level_above(cores, multilayer_graph):
    count = {}
    for v, c in cores.items():  
        for n in multilayer_graph.get_nodes():
            if n in c:
                if n not in count:
                    count[n] = 1
                else:
                    count[n] += 1
    return count