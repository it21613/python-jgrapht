from collections import defaultdict
from collections.abc import (
    Set,
    MutableMapping,
)
import copy

from .. import backend
from ..types import (
    Graph,
    GraphEvent,
    AttributesGraph,
    DirectedAcyclicGraph,
    ListenableGraph,
)

from ._graphs import create_int_graph as _create_int_graph, create_int_dag as _create_int_dag
from ._views import (
    _ListenableView,
    _UnweightedGraphView,
    _UndirectedGraphView,
    _UnmodifiableGraphView,
    _EdgeReversedGraphView,
    _WeightedView,
    _MaskedSubgraphView,
)
from ._attrsg_collections import (
    _AttributesGraphVertexSet,
    _AttributesGraphVertexIterator,
    _AttributesGraphEdgeIterator,
)


class _AttributesGraph(Graph, AttributesGraph, ListenableGraph):
    """An attributes graph allows the use of any hashable as vertex and edges.
    
    This is a wrapper around the default graph which has integer identifiers, 
    which means that there is a performance penalty involved. The graph also 
    supports attributes on graph vertices/edges and the graph itself.

    This graph does not directly wrap a backend graph, but it passes through 
    the handle which means that it is usable in all algorithms. The result 
    however will refer to the actual graph and not the attributes graph wrapper which
    means that it needs to be translated back when returning from the call.
    Most algorithms do such a check and perform the translation automatically.
    """

    def __init__(
        self, graph, vertex_supplier=None, edge_supplier=None, copy_from=None, **kwargs
    ):
        """Initialize an attributes graph

        :param graph: the actual graph which we are wrapping. Must have integer 
          vertices and edges.
        :param vertex_supplier: function which returns new vertices on each call. If
          None then object instances are used.
        :param edge_supplier: function which returns new edge on each call. If
          None then object instances are used.
        :param copy_from: copy from another graph
        """
        self._graph = graph
        self._vertex_set = None
        self._edge_set = None

        # setup structural events callback
        def structural_cb(element, event_type):
            self._structural_event_listener(element, event_type)

        self._listenable_graph = _ListenableView(graph)
        self._listenable_graph.add_listener(structural_cb)
        self._user_listeners = []

        if copy_from is not None:
            # copy suppliers
            self._vertex_supplier = copy_from._vertex_supplier
            self._edge_supplier = copy_from._edge_supplier

            # copy vertex maps
            self._vertex_hash_to_id = copy_from._vertex_hash_to_id
            self._vertex_id_to_hash = copy_from._vertex_id_to_hash
            self._vertex_hash_to_props = copy_from._vertex_hash_to_props
            self._vertex_props = self._VertexAttributes(
                self, self._vertex_hash_to_props
            )

            # copy edge maps
            self._edge_hash_to_id = copy_from._edge_hash_to_id
            self._edge_id_to_hash = copy_from._edge_id_to_hash
            self._edge_hash_to_props = copy_from._edge_hash_to_props
            self._edge_props = self._EdgeAttributes(self, self._edge_hash_to_props)

            # initialize graph maps
            self._graph_props = copy_from._graph_props

        else:
            # initialize suppliers
            if vertex_supplier is None:
                vertex_supplier = lambda: object()
            self._vertex_supplier = vertex_supplier
            if edge_supplier is None:
                edge_supplier = lambda: object()
            self._edge_supplier = edge_supplier

            # initialize vertex maps
            self._vertex_hash_to_id = {}
            self._vertex_id_to_hash = {}
            self._vertex_hash_to_props = defaultdict(lambda: {})
            self._vertex_props = self._VertexAttributes(
                self, self._vertex_hash_to_props
            )

            # initialize edge maps
            self._edge_hash_to_id = {}
            self._edge_id_to_hash = {}
            self._edge_hash_to_props = defaultdict(lambda: {})
            self._edge_props = self._EdgeAttributes(self, self._edge_hash_to_props)

            # initialize graph maps
            self._graph_props = {}

    @property
    def handle(self):
        # Handle to the backend graph. We return the listenable graph
        # in order to track any changes, happening outside the graph.
        return self._listenable_graph.handle

    @property
    def type(self):
        return self._graph.type

    @property
    def vertex_supplier(self):
        """The vertex supplier."""
        return self._vertex_supplier

    @property
    def edge_supplier(self):
        """The edge supplier."""
        return self._edge_supplier

    def add_vertex(self, vertex=None):
        if vertex is not None and vertex in self.vertices:
            return vertex
        vid = self._graph.add_vertex()
        vertex = self._add_new_vertex(vid, vertex)
        for listener in self._user_listeners:
            listener(vertex, GraphEvent.VERTEX_ADDED)
        return vertex

    def remove_vertex(self, v):
        if v is None:
            raise ValueError("Vertex cannot be None")
        vid = self._vertex_hash_to_id.get(v)
        if vid is None:
            return False
        # Call on listenable graph, as it might remove edges also.
        self._listenable_graph.remove_vertex(vid)
        return True

    def contains_vertex(self, v):
        return v in self.vertices

    def add_edge(self, u, v, weight=None, edge=None):
        if edge is not None and edge in self.edges:
            return edge

        eid = self._graph.add_edge(self._get_vertex_id(u), self._get_vertex_id(v))
        edge = self._add_new_edge(eid, edge)

        for listener in self._user_listeners:
            listener(edge, GraphEvent.EDGE_ADDED)

        if weight is not None:
            self._listenable_graph.set_edge_weight(eid, weight)

        return edge

    def remove_edge(self, e):
        if e is None:
            raise ValueError("Edge cannot be None")
        eid = self._edge_hash_to_id.get(e)
        if eid is None:
            return False
        self._listenable_graph.remove_edge(eid)
        return True

    def contains_edge(self, e):
        return e in self.edges

    def contains_edge_between(self, u, v):
        return self._listenable_graph.contains_edge_between(
            self._get_vertex_id(u), self._get_vertex_id(v)
        )

    def degree_of(self, v):
        return self._listenable_graph.degree_of(self._get_vertex_id(v))

    def indegree_of(self, v):
        return self._listenable_graph.indegree_of(self._get_vertex_id(v))

    def outdegree_of(self, v):
        return self._listenable_graph.outdegree_of(self._get_vertex_id(v))

    def edge_source(self, e):
        vid = self._listenable_graph.edge_source(self._get_edge_id(e))
        return self._vertex_id_to_hash[vid]

    def edge_target(self, e):
        vid = self._listenable_graph.edge_target(self._get_edge_id(e))
        return self._vertex_id_to_hash[vid]

    def get_edge_weight(self, e):
        return self._listenable_graph.get_edge_weight(self._get_edge_id(e))

    def set_edge_weight(self, e, weight):
        self._listenable_graph.set_edge_weight(self._get_edge_id(e), weight)

    @property
    def number_of_vertices(self):
        return len(self.vertices)

    @property
    def vertices(self):
        if self._vertex_set is None:
            self._vertex_set = self._AttributesGraphVertexSet(self)
        return self._vertex_set

    @property
    def number_of_edges(self):
        return len(self.edges)

    @property
    def edges(self):
        if self._edge_set is None:
            self._edge_set = self._AttributesGraphEdgeSet(self)
        return self._edge_set

    def edges_between(self, u, v):
        it = self._listenable_graph.edges_between(
            self._get_vertex_id(u), self._get_vertex_id(v)
        )
        return self._create_edge_it(it)

    def edges_of(self, v):
        it = self._listenable_graph.edges_of(self._get_vertex_id(v))
        return self._create_edge_it(it)

    def inedges_of(self, v):
        it = self._listenable_graph.inedges_of(self._get_vertex_id(v))
        return self._create_edge_it(it)

    def outedges_of(self, v):
        it = self._listenable_graph.outedges_of(self._get_vertex_id(v))
        return self._create_edge_it(it)

    @property
    def graph_attrs(self):
        return self._graph_props

    @property
    def vertex_attrs(self):
        return self._vertex_props

    @property
    def edge_attrs(self):
        return self._edge_props

    def add_listener(self, listener_cb):
        self._user_listeners.append(listener_cb)
        return listener_cb

    def remove_listener(self, listener_cb):
        self._user_listeners.remove(listener_cb)

    def __repr__(self):
        return "_AttributesGraph(%r)" % self._graph.handle

    def _get_vertex_id(self, v):
        vid = self._vertex_hash_to_id.get(v)
        if vid is None:
            raise ValueError("Vertex {} not in graph".format(v))
        return vid

    def _get_edge_id(self, e):
        eid = self._edge_hash_to_id.get(e)
        if eid is None:
            raise ValueError("Edge {} not in graph".format(e))
        return eid

    def _create_edge_it(self, edge_id_it):
        """Transform an integer edge iteration into an edge iterator."""
        for eid in edge_id_it:
            yield self._edge_id_to_hash[eid]

    def _add_new_vertex(self, vid, vertex=None):
        if vertex is None:
            vertex = self._vertex_supplier()
        if vertex in self._vertex_hash_to_id:
            raise ValueError("Vertex supplier returns vertices already in the graph")
        self._vertex_hash_to_id[vertex] = vid
        self._vertex_id_to_hash[vid] = vertex
        return vertex

    def _add_new_edge(self, eid, edge=None):
        if edge is None:
            edge = self._edge_supplier()
        if edge in self._edge_hash_to_id:
            raise ValueError("Edge supplier returns edges already in the graph")
        self._edge_hash_to_id[edge] = eid
        self._edge_id_to_hash[eid] = edge
        return edge

    def _remove_vertex(self, vid):
        v = self._vertex_id_to_hash.pop(vid)
        self._vertex_hash_to_id.pop(v)
        self._vertex_hash_to_props.pop(v, None)
        return v

    def _remove_edge(self, eid):
        e = self._edge_id_to_hash.pop(eid)
        self._edge_hash_to_id.pop(e)
        self._edge_hash_to_props.pop(e, None)
        return e

    def _structural_event_listener(self, element, event_type):
        """Listener for removal events. This is needed, as removing
        a graph vertex might also remove edges.
        """
        # perform changes in the attributes graph
        if event_type == GraphEvent.VERTEX_ADDED:
            self._add_new_vertex(element)
            for listener in self._user_listeners:
                listener(self._vertex_id_to_hash[element], event_type)
        elif event_type == GraphEvent.VERTEX_REMOVED:
            v = self._remove_vertex(element)
            for listener in self._user_listeners:
                listener(v, event_type)
        elif event_type == GraphEvent.EDGE_ADDED:
            self._add_new_edge(element)
            for listener in self._user_listeners:
                listener(self._edge_id_to_hash[element], event_type)
        elif event_type == GraphEvent.EDGE_REMOVED:
            e = self._remove_edge(element)
            for listener in self._user_listeners:
                listener(e, event_type)
        elif event_type == GraphEvent.EDGE_WEIGHT_UPDATED:
            e = self._edge_id_to_hash[element]
            for listener in self._user_listeners:
                listener(e, event_type)

    class _AttributesGraphVertexSet(Set):
        def __init__(self, graph):
            self._graph = graph
            self._handle = graph.handle

        def __iter__(self):
            res = backend.jgrapht_graph_create_all_vit(self._handle)
            return _AttributesGraphVertexIterator(res, self._graph)

        def __len__(self):
            return backend.jgrapht_graph_vertices_count(self._handle)

        def __contains__(self, v):
            v = self._graph._vertex_hash_to_id.get(v)
            if v is None:
                return False
            # important to do both checks here, as some views might share
            # the _vertex_hash_to_id dictionary
            return backend.jgrapht_graph_contains_vertex(self._handle, v)

        def __repr__(self):
            return "_AttributesGraphVertexSet(%r)" % self._handle

        def __str__(self):
            return "{" + ", ".join(str(x) for x in self) + "}"

    class _AttributesGraphEdgeSet(Set):
        def __init__(self, graph):
            self._graph = graph
            self._handle = graph.handle

        def __iter__(self):
            res = backend.jgrapht_graph_create_all_eit(self._handle)
            return _AttributesGraphEdgeIterator(res, self._graph)

        def __len__(self):
            return backend.jgrapht_graph_edges_count(self._handle)

        def __contains__(self, e):
            e = self._graph._edge_hash_to_id.get(e)
            if e is None:
                return False
            # important to do both checks here, as some views might share
            # the _edge_hash_to_id dictionary
            return backend.jgrapht_graph_contains_edge(self._handle, e)

        def __repr__(self):
            return "_AttributesGraphEdgeSet(%r)" % self._handle

        def __str__(self):
            return "{" + ", ".join(str(x) for x in self) + "}"

    class _VertexAttributes(MutableMapping):
        """Wrapper around a dictionary to ensure vertex existence."""

        def __init__(self, graph, storage):
            self._graph = graph
            self._storage = storage

        def __getitem__(self, key):
            if key not in self._graph.vertices:
                raise ValueError("Vertex {} not in graph".format(key))
            return self._storage[key]

        def __setitem__(self, key, value):
            if key not in self._graph.vertices:
                raise ValueError("Vertex {} not in graph".format(key))
            self._storage[key] = value

        def __delitem__(self, key):
            if key not in self._graph.vertices:
                raise ValueError("Vertex {} not in graph".format(key))
            del self._storage[key]

        def __len__(self):
            return len(self._storage)

        def __iter__(self):
            return iter(self._storage)

        def __repr__(self):
            return "_AttributesGraph-VertexAttributes(%r)" % repr(self._storage)

        def __str__(self):
            items = []
            for v in self._graph.vertices:
                items.append("{}: {}".format(v, self._storage[v]))
            return "{" + ", ".join(items) + "}"

    class _EdgeAttributes(MutableMapping):
        """Wrapper around a dictionary to ensure edge existence."""

        def __init__(self, graph, storage):
            self._graph = graph
            self._storage = storage

        def __getitem__(self, key):
            if key not in self._graph.edges:
                raise ValueError("Edge {} not in graph".format(key))
            return self._graph._PerEdgeWeightAwareDict(
                self._graph, key, self._storage[key]
            )

        def __setitem__(self, key, value):
            if key not in self._graph.edges:
                raise ValueError("Edge {} not in graph".format(key))
            self._storage[key] = value

        def __delitem__(self, key):
            if key not in self._graph.edges:
                raise ValueError("Edge {} not in graph".format(key))
            del self._storage[key]

        def __len__(self):
            return len(self._storage)

        def __iter__(self):
            return iter(self._storage)

        def __repr__(self):
            return "_AttributesGraph-EdgeAttributes(%r)" % repr(self._storage)

        def __str__(self):
            items = []
            for e in self._graph.edges:
                items.append("{}: {}".format(e, self._storage[e]))
            return "{" + ", ".join(items) + "}"

    class _PerEdgeWeightAwareDict(MutableMapping):
        """A dictionary view which knows about the special key weight and delegates
        to the graph. This is only a view."""

        def __init__(self, graph, edge, storage, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._graph = graph
            self._edge = edge
            self._storage = storage

        def __getitem__(self, key):
            if key is "weight":
                return self._graph.get_edge_weight(self._edge)
            else:
                return self._storage[key]

        def __setitem__(self, key, value):
            if key is "weight":
                if not isinstance(value, (float)):
                    raise TypeError("Weight is not a floating point number")
                self._graph.set_edge_weight(self._edge, value)
            else:
                self._storage[key] = value

        def __delitem__(self, key):
            if key is "weight":
                self._graph.set_edge_weight(self._edge, 1.0)
            else:
                del self._storage[key]

        def __len__(self):
            return len(self._storage)

        def __iter__(self):
            return iter(self._storage)

        def __repr__(self):
            return "_PerEdgeWeightAwareDict(%r, %r, %r)" % (
                repr(self._graph),
                repr(self._edge),
                repr(self._storage),
            )

        def __str__(self):
            return str(self._storage)


class _AttributesDirectedAcyclicGraph(_AttributesGraph, DirectedAcyclicGraph):
    """The directed acyclic graph wrapper."""

    def __init__(self, graph, vertex_supplier=None, edge_supplier=None, **kwargs):
        """Initialize an attributes graph

        :param graph: the actual graph which we are wrapping. Must have integer 
          vertices and edges.
        :param vertex_supplier: function which returns new vertices on each call. If
          None then object instances are used.
        :param edge_supplier: function which returns new edge on each call. If
          None then object instances are used.
        """
        super().__init__(
            graph=graph,
            vertex_supplier=vertex_supplier,
            edge_supplier=edge_supplier,
            **kwargs
        )

    def descendants(self, v):
        vid = self._vertex_hash_to_id.get(v)
        if vid is None:
            raise ValueError("Vertex {} not in graph".format(v))
        set_handle = backend.jgrapht_graph_dag_vertex_descendants(self.handle, vid)
        return _AttributesGraphVertexSet(set_handle, self)

    def ancestors(self, v):
        vid = self._vertex_hash_to_id.get(v)
        if vid is None:
            raise ValueError("Vertex {} not in graph".format(v))
        set_handle = backend.jgrapht_graph_dag_vertex_ancestors(self.handle, vid)
        return _AttributesGraphVertexSet(set_handle, self)

    def __iter__(self):
        it_handle = backend.jgrapht_graph_dag_topological_it(self.handle)
        return _AttributesGraphVertexIterator(it_handle, self)


class _MaskedSubgraphAttributesGraph(_AttributesGraph):
    """A masked subgraph attributes graph."""

    def __init__(
        self,
        graph,
        vertex_supplier,
        edge_supplier,
        copy_from,
        vertex_mask_cb,
        edge_mask_cb,
        **kwargs
    ):
        assert isinstance(
            graph, _MaskedSubgraphView
        ), "Can only be used with a masked subgraph backend"

        super().__init__(graph, vertex_supplier, edge_supplier, copy_from)
        self._vertex_mask_cb = vertex_mask_cb
        self._edge_mask_cb = edge_mask_cb

    def add_vertex(self, vertex=None):
        raise ValueError("this graph is unmodifiable")

    def remove_vertex(self, v):
        raise ValueError("this graph is unmodifiable")

    def contains_vertex(self, v):
        return v in self.vertices and not self._vertex_mask_cb(v)

    def add_edge(self, u, v, weight=None, edge=None):
        raise ValueError("this graph is unmodifiable")

    def remove_edge(self, e):
        raise ValueError("this graph is unmodifiable")

    def contains_edge(self, e):
        return e in self.edges and not self._edge_mask_cb(e)

    def __repr__(self):
        return "_MaskedSubgraphAttributesGraph(%r)" % self._graph.handle

    def _get_vertex_id(self, v):
        vid = self._vertex_hash_to_id.get(v)
        if vid is None or self._vertex_mask_cb(v):
            raise ValueError("Vertex {} not in graph".format(v))
        return vid

    def _get_edge_id(self, e):
        eid = self._edge_hash_to_id.get(e)
        if eid is None or self._edge_mask_cb(e):
            raise ValueError("Edge {} not in graph".format(e))
        return eid


def _create_attrs_graph_subgraph(
    attrs_graph, subgraph
):
    """Create an attributes graph subgraph.

    This function create an attributes graph with the identical structure as the
    subgraph (which is a normal graph with integer vertices/edges). The assumption
    is that the subgraph is actual subgraph of the backing graph of the attributes
    graph. In other words, for each integer vertex or edge in the subgraph, the 
    attributes graph contains a corresponding vertex or edge.
    
    The new attributes graph uses the same vertices and edges that the attributes graph
    is using and has the same structure as the subgraph. However, its backing graph 
    is a copy and therefore might have different integer vertices/edges.

    :param attrs_graph: the attributes graph from which to copy vertices and edges
    :param subgraph: the subgraph (must be a backend _JGraphTGraph)
    """
    res = create_attrs_graph(
        directed=subgraph.type.directed,
        allowing_self_loops=subgraph.type.allowing_self_loops,
        allowing_multiple_edges=subgraph.type.allowing_multiple_edges,
        weighted=subgraph.type.weighted,
        vertex_supplier=attrs_graph.vertex_supplier,
        edge_supplier=attrs_graph.edge_supplier,
    )

    vertex_map = {}
    for vid in subgraph.vertices:
        v = vertex_g_to_attrsg(attrs_graph, vid)
        res.add_vertex(vertex=v)
        res.vertex_attrs[v] = copy.copy(attrs_graph.vertex_attrs[v])
        vertex_map[vid] = v

    weighted = subgraph.type.weighted
    for eid in subgraph.edges:
        e = edge_g_to_attrsg(attrs_graph, eid)
        s, t, w = subgraph.edge_tuple(eid)
        if weighted:
            res.add_edge(vertex_map[s], vertex_map[t], weight=w, edge=e)
        else:
            res.add_edge(vertex_map[s], vertex_map[t], edge=e)
        res.edge_attrs[e] = copy.copy(attrs_graph.edge_attrs[e])

    return res


def as_unweighted_attrs_graph(attrs_graph):
    """Create an unweighted view of an attributes graph."""
    graph = attrs_graph._graph
    unweighted_graph = _UnweightedGraphView(graph)

    unweighted_attrs_graph = _AttributesGraph(
        unweighted_graph, copy_from=attrs_graph
    )

    return unweighted_attrs_graph


def as_undirected_attrs_graph(attrs_graph):
    """Create an undirected view of an attributes graph."""
    graph = attrs_graph._graph
    undirected_graph = _UndirectedGraphView(graph)

    undirected_attrs_graph = _AttributesGraph(
        undirected_graph, copy_from=attrs_graph
    )

    return undirected_attrs_graph


def as_unmodifiable_attrs_graph(attrs_graph):
    """Create an unmodifiable view of an attributes graph."""
    graph = attrs_graph._graph
    unmodifiable_graph = _UnmodifiableGraphView(graph)

    unmodifiable_attrs_graph = _AttributesGraph(
        unmodifiable_graph, copy_from=attrs_graph
    )

    return unmodifiable_attrs_graph


def as_edgereversed_attrs_graph(attrs_graph):
    """Create an edge reversed view of an attributes graph."""
    graph = attrs_graph._graph
    edgereversed_graph = _EdgeReversedGraphView(graph)

    edgereversed_attrs_graph = _AttributesGraph(
        edgereversed_graph, copy_from=attrs_graph
    )

    return edgereversed_attrs_graph


def as_weighted_attrs_graph(
    attrs_graph, edge_weight_cb, cache_weights, write_weights_through
):
    """Create a weighted view of an attributes graph."""
    if edge_weight_cb is not None:
        def actual_edge_weight_cb(e):
            e = edge_g_to_attrsg(attrs_graph, e)
            return edge_weight_cb(e)
    else:
        actual_edge_weight_cb = None

    graph = attrs_graph._graph
    weighted_graph = _WeightedView(
        graph, actual_edge_weight_cb, cache_weights, write_weights_through
    )

    weighted_attrs_graph = _AttributesGraph(weighted_graph, copy_from=attrs_graph)
    return weighted_attrs_graph


def as_masked_subgraph_attrs_graph(
    attrs_graph, vertex_mask_cb, edge_mask_cb=None
):
    """ Create a masked subgraph view of an attributes graph."""
    def actual_vertex_mask_cb(v):
        v = vertex_g_to_attrsg(attrs_graph, v)
        return vertex_mask_cb(v)

    if edge_mask_cb is not None:
        def actual_edge_mask_cb(e):
            e = edge_g_to_attrsg(attrs_graph, e)
            return edge_mask_cb(e)
    else:
        actual_edge_mask_cb = None

    graph = attrs_graph._graph
    masked_subgraph = _MaskedSubgraphView(
        graph, actual_vertex_mask_cb, actual_edge_mask_cb
    )

    masked_subgraph_attrs_graph = _MaskedSubgraphAttributesGraph(
        masked_subgraph,
        vertex_supplier=None,
        edge_supplier=None,
        copy_from=attrs_graph,
        vertex_mask_cb=vertex_mask_cb,
        edge_mask_cb=edge_mask_cb,
    )

    return masked_subgraph_attrs_graph


def is_attrs_graph(graph):
    """Check if a graph instance is an attributes graph.
    
    :param graph: the graph
    :returns: True if the graph is an attributes graph, False otherwise.
    """
    return isinstance(graph, (_AttributesGraph, AttributesGraph))


def vertex_attrsg_to_g(graph, vertex):
    """Translate from an attributes graph vertex to a graph vertex."""
    if is_attrs_graph(graph):
        return graph._vertex_hash_to_id[vertex] if vertex is not None else None
    return vertex


def vertex_g_to_attrsg(graph, vertex):
    """Translate from a graph vertex to an attributes graph vertex."""
    if is_attrs_graph(graph):
        return graph._vertex_id_to_hash[vertex] if vertex is not None else None
    return vertex


def edge_attrsg_to_g(graph, edge):
    """Translate from an attributes graph edge to a graph edge."""
    if is_attrs_graph(graph):
        return graph._edge_hash_to_id[edge] if edge is not None else None
    return edge


def edge_g_to_attrsg(graph, edge):
    """Translate from a graph edge to an attributes graph edge."""
    if is_attrs_graph(graph):
        return graph._edge_id_to_hash[edge] if edge is not None else None
    return edge


def create_attrs_graph(
    directed=True,
    allowing_self_loops=False,
    allowing_multiple_edges=False,
    weighted=True,
    vertex_supplier=None,
    edge_supplier=None,
):
    """Create an attributes graph.

    :param directed: if True the graph will be directed, otherwise undirected
    :param allowing_self_loops: if True the graph will allow the addition of self-loops
    :param allowing_multiple_edges: if True the graph will allow multiple-edges
    :param weighted: if True the graph will be weighted, otherwise unweighted
    :param vertex_supplier: function which returns new vertices on each call. If
        None then object instances are used.
    :param edge_supplier: function which returns new edges on each call. If
        None then object instances are used.    
    :returns: a graph
    :rtype: :class:`~jgrapht.types.AttributesGraph`    
    """
    g = _create_int_graph(
        directed=directed,
        allowing_self_loops=allowing_self_loops,
        allowing_multiple_edges=allowing_multiple_edges,
        weighted=weighted,
    )
    return _AttributesGraph(
        g, vertex_supplier=vertex_supplier, edge_supplier=edge_supplier
    )


def create_directed_attrs_graph(
    allowing_self_loops=False,
    allowing_multiple_edges=False,
    weighted=True,
    vertex_supplier=None,
    edge_supplier=None,
):
    """Create a directed attributes graph.

    :param allowing_self_loops: if True the graph will allow the addition of self-loops
    :param allowing_multiple_edges: if True the graph will allow multiple-edges
    :param weighted: if True the graph will be weighted, otherwise unweighted
    :param vertex_supplier: function which returns new vertices on each call. If
        None then object instances are used.
    :param edge_supplier: function which returns new edge on each call. If
        None then object instances are used.        
    :returns: a graph
    :rtype: :class:`~jgrapht.types.AttributesGraph`    
    """
    return create_attrs_graph(
        directed=True,
        allowing_self_loops=allowing_self_loops,
        allowing_multiple_edges=allowing_multiple_edges,
        weighted=weighted,
        vertex_supplier=vertex_supplier,
        edge_supplier=edge_supplier,
    )


def create_undirected_attrs_graph(
    allowing_self_loops=False,
    allowing_multiple_edges=False,
    weighted=True,
    vertex_supplier=None,
    edge_supplier=None,
):
    """Create an undirected attributes graph.

    :param allowing_self_loops: if True the graph will allow the addition of self-loops
    :param allowing_multiple_edges: if True the graph will allow multiple-edges
    :param weighted: if True the graph will be weighted, otherwise unweighted
    :param vertex_supplier: function which returns new vertices on each call. If
        None then object instances are used.
    :param edge_supplier: function which returns new edge on each call. If
        None then object instances are used.        
    :returns: a graph
    :rtype: :class:`~jgrapht.types.AttributesGraph`    
    """
    return create_attrs_graph(
        directed=False,
        allowing_self_loops=allowing_self_loops,
        allowing_multiple_edges=allowing_multiple_edges,
        weighted=weighted,
        vertex_supplier=vertex_supplier,
        edge_supplier=edge_supplier,
    )


def create_attrs_dag(
    allowing_multiple_edges=False,
    weighted=True,
    vertex_supplier=None,
    edge_supplier=None,
):
    """Create a directed acyclic attributes graph.

    :param allowing_multiple_edges: if True the graph will allow multiple-edges
    :param weighted: if True the graph will be weighted, otherwise unweighted
    :param vertex_supplier: function which returns new vertices on each call. If
        None then object instances are used.
    :param edge_supplier: function which returns new edge on each call. If
        None then object instances are used.        
    :returns: a graph
    :rtype: :class:`~jgrapht.types.DirectedAcyclicGraph` and :class:`~jgrapht.types.AttributesGraph`
    """
    g = _create_int_dag(allowing_multiple_edges=allowing_multiple_edges, weighted=weighted)
    return _AttributesDirectedAcyclicGraph(
        g, vertex_supplier=vertex_supplier, edge_supplier=edge_supplier
    )
