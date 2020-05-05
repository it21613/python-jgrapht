import pytest

from jgrapht import create_graph
from jgrapht.io.exporters import write_dot
from jgrapht.io.importers import read_dot, parse_dot



def build_graph():
    g = create_graph(directed=False, allowing_self_loops=False, allowing_multiple_edges=False, weighted=True)

    g.add_vertex()
    g.add_vertex()
    g.add_vertex()

    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 2)

    return g


def test_output_gml(tmpdir):

    g = build_graph()
    tmpfile = tmpdir.join('dot.out')
    tmpfilename = str(tmpfile)

    v_dict = { 
        0: { 'name': 'name 0' }, 
	    1: { 'name': 'name 1' }, 
		2: { 'name': 'name 2' }, 
	}

    e_dict = { 
        0: { 'label': 'ακμή 1-2' } 
    }

    write_dot(g, tmpfilename, per_vertex_attrs_dict=v_dict, per_edge_attrs_dict=e_dict)

    # read back 

    def ea_cb(edge, attribute_name, attribute_value):
        if edge == 0: 
            if attribute_name == 'label': 
                assert attribute_value == 'ακμή 1-2'

    g1 = create_graph(directed=False, allowing_self_loops=False, allowing_multiple_edges=False, weighted=True)
    read_dot(g1, tmpfilename, edge_attribute_cb=ea_cb)

    assert len(g1.vertices()) == 3
    assert len(g1.edges()) == 3

    #assert 0


