from . import jgrapht
from . import status
from . import errors

class GraphType: 

    def __init__(self, directed, allowing_self_loops, allowing_multiple_edges, weighted):
        self.__directed = directed
        self.__allowing_self_loops = allowing_self_loops
        self.__allowing_multiple_edges = allowing_multiple_edges
        self.__weighed = weighted

    @property
    def directed(self):
        return self.__directed

    @property
    def undirected(self):
        return not self.__directed    

    @property
    def allowing_self_loops(self):
        return self.__allowing_self_loops

    @property
    def allowing_multiple_edges(self):
        return self.__allowing_multiple_edges

    @property
    def weighted(self):
        return self.__weighted

    def __str__(self):
        return '(directed={}, self-loops={}, multiple-edges={}, weighted={})' \
            .format(self.__directed, self.__allowing_self_loops, self.__allowing_multiple_edges, self.__weighed )


class Graph:

    def __init__(self):
        self.__g_handle = jgrapht.jgrapht_create_graph(1,1,1)
        self.__graph_type = GraphType(True, True, True, True)
        errors.check_last_error()

    @property
    def graph_type(self):
        return self.__graph_type;

    def add_vertex(self):
        v = jgrapht.jgrapht_graph_add_vertex(self.__g_handle)
        errors.check_last_error()
        return v

    def remove_vertex(self, vertex):
        res = jgrapht.jgrapht_graph_remove_vertex(self.__g_handle, vertex)
        errors.check_last_error()
        return res 

    def contains_vertex(self, vertex):
        res = jgrapht.jgrapht_graph_contains_vertex(self.__g_handle, vertex)
        errors.check_last_error()
        return res 

    def vertices_count(self):
        res = jgrapht.jgrapht_graph_vertices_count(self.__g_handle)
        errors.check_last_error()        
        return res 

    def add_edge(self, source, target):
        e = jgrapht.jgrapht_graph_add_edge(self.__g_handle, source, target)
        errors.check_last_error()
        return e

    def remove_edge(self, edge): 
        res = jgrapht.jgrapht_graph_remove_edge(self.__g_handle, edge)
        errors.check_last_error()
        return res

    def contains_edge(self, edge):
        res = jgrapht.jgrapht_graph_contains_edge(self.__g_handle, edge)
        errors.check_last_error()
        return res     

    def edges_count(self):
        res = jgrapht.jgrapht_graph_edges_count(self.__g_handle)
        errors.check_last_error()        
        return res     

    def degree_of(self, vertex):
        res = jgrapht.jgrapht_graph_degree_of(self.__g_handle, vertex)
        errors.check_last_error()        
        return res     

    def indegree_of(self, vertex):
        res = jgrapht.jgrapht_graph_indegree_of(self.__g_handle, vertex)
        errors.check_last_error()        
        return res

    def outdegree_of(self, vertex):
        res = jgrapht.jgrapht_graph_outdegree_of(self.__g_handle, vertex)
        errors.check_last_error()        
        return res

    def edge_source(self, edge):
        res = jgrapht.jgrapht_graph_edge_source(self.__g_handle, edge)
        errors.check_last_error()
        return res

    def edge_target(self, edge):
        res = jgrapht.jgrapht_graph_edge_target(self.__g_handle, edge)
        errors.check_last_error()
        return res

    def get_edge_weight(self, edge): 
        res = jgrapht.jgrapht_graph_get_edge_weight(self.__g_handle, edge)
        errors.check_last_error()
        return res

    def set_edge_weight(self, edge, weight): 
        jgrapht.jgrapht_graph_set_edge_weight(self.__g_handle, edge, weight)
        errors.check_last_error()

    
