# -*- coding: utf-8 -*-

"""
Node Colormap
=============================

In this example we draw a graph with matplotlib using the circular layout,
coloring vertices by degree. You must have matplotlib for this to work.
"""

# %%
# Start by importing the package
import jgrapht
import jgrapht.drawing.draw_matplotlib as draw_matplotlib
import matplotlib.pyplot as plt


# %%
# Creating a graph

g = jgrapht.create_graph(directed=False, weighted=True,)


# %%
# Add some vertices
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()
g.add_vertex()


# %%
# and some edges
e1 = g.add_edge(0, 1)
e2 = g.add_edge(0, 2)
e3 = g.add_edge(0, 3)
e4 = g.add_edge(0, 4)
e5 = g.add_edge(0, 5)
e6 = g.add_edge(0, 6)
e7 = g.add_edge(0, 7)
e8 = g.add_edge(0, 8)
e9 = g.add_edge(0, 9)

# %%
# Compute the position of the vertices
pos = draw_matplotlib.layout(g, pos_layout="circular_layout")

# %%
# Draw the graph using the node labels,edge labels and node colormap
draw_matplotlib.draw_jgrapht(
    g,
    position=pos,
    edge_label=True,
    node_color=range(len(g.vertices)),
    node_cmap=plt.cm.Oranges,
    axis=False,
)
plt.show()