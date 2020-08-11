import jgrapht
from matplotlib.patches import FancyArrowPatch


def draw_jgrapht(
    g, position=None, arrow=False, node_label=False, edge_label=False, **kwargs
):
    """
    Parameters:
                See draw_nodes,draw_edges,Only_Lables
                :param g: graph
                :param position: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                :type position: dictionary, optional
                :param arrow: draw arrowheads
                :type arrow:bool, optional (default=True)
                :param node_label:draw labels on the nodes.
                :type node_label: bool, optional (default=False)
                :param edge_label:draw labels on the edges
                :type edge_label: bool, optional (default=False)
                :param kwargs:See draw_nodes,draw_edges,draw_Lables,draw_edge_labels
                :type kwargs:optional keywords
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib required for draw()") from e
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise
    show = 0

    if position is None:
        position = layout(g)

    draw_nodes(
        g, position, node_label=node_label, show=show, **kwargs
    )  # Draw the nodes
    draw_edges(
        g,
        position,
        arrow=arrow,
        edge_label=edge_label,
        node_label=node_label,
        show=show,
        **kwargs,
    )  # Draw the edges

    if node_label is True:
        draw_labels(g, position=position, **kwargs)  # Draw lables of nodes

    if edge_label is True:
        draw_edge_labels(g, position=position, **kwargs)  # Draw lables of edges

    plt.draw_if_interactive()


def draw_nodes(
    g,
    position,
    axis=False,
    node_linewidths=1.0,
    node_title=None,
    node_size=450,
    node_color="green",
    node_cmap=None,
    vmin=None,
    vmax=None,
    node_shape="o",
    node_edge_color="face",
    node_list=None,
    alpha=1,
    node_label=False,
    ax=None,
    **kwargs
):
    """
          Parameters:
                    :param g: graph
                    :param position: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                    :type position: dictionary, optional
                    :param axis:Draw the axes
                    :type axis:bool, optional (default=False)
                    :param node_linewidths:Line width of symbol border
                    :type node_linewidths:float,(default:1.0)
                    :param node_title:Label for graph legend
                    :type node_title:list, optional  (default:None)
                    :param node_size: Size of nodes
                    :type node_size: scalar or array, optional (default=500)
                    :param node_color:Node color
                    :type node_color: color or array of colors (default='green')
                    :param node_cmap:Colormap for mapping intensities of nodes
                    :type node_cmap: Matplotlib colormap, optional (default=None | example:node_cmap=plt.cm.Greens)
                    :param vmin:Minimum for node colormap scaling
                    :type vmin:float, optional (default=None)
                    :param vmax:Maximum for node colormap scaling
                    :type vmax:float, optional (default=None)
                    :param node_shape:The shape of the node
                    :type node_shape:string, optional (default='o')
                    :param node_edge_color:color the edge of node
                    :type node_edge_color:string, optional (default='face')
                    :param node_list: Draw only specified nodes
                    :type node_list: list, optional (default: node_list=None)
                    :param alpha:The node transparency
                    :type alpha: float, optional (default=1.0)
                    :param node_label:draw labels on the nodes.
                    :type node_label: bool, optional (default=False)
                    :param ax: Draw the graph in the specified Matplotlib axes
                    :type ax:Matplotlib Axes object, optional
                    :param kwargs:See draw_jgrapht
                    :type kwargs:optional keywords
          """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib required for draw()") from e
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()
    if axis is False:
        ax.set_axis_off()

    positionlist = list(zip(*position))  # seperate x from  y
    if node_list is None:  # Draw all nodes
        # Draw nodes
        ax.scatter(
            positionlist[0],
            positionlist[1],
            c=node_color,
            alpha=alpha,
            linewidth=node_linewidths,
            s=node_size,
            cmap=node_cmap,
            vmin=vmin,
            vmax=vmax,
            marker=node_shape,
            edgecolors=node_edge_color,
            zorder=2.5,
            label=node_title,
        )
        if node_title is not None:
            # Draw Legend graph for node
            handles, labels = ax.get_legend_handles_labels()
            unique = [
                (h, l)
                for i, (h, l) in enumerate(zip(handles, labels))
                if l not in labels[:i]
            ]
            ax.legend(
                *zip(*unique),
                loc="upper center",
                fancybox=True,
                framealpha=1,
                shadow=True,
                borderpad=0.3,
                markerscale=0.5,
                markerfirst=True,
                ncol=3,
                bbox_to_anchor=(0.5, 1.15),
            )

    elif node_list is not None:  # Draw specific nodes
        positionlist.clear()
        for i, vertex in enumerate(node_list):
            positionlist.append(list(zip(position[node_list[i]])))

        # seperate x from  y
        positionlist = list(zip(*positionlist))
        # Draw the specific nodes
        ax.scatter(
            positionlist[0],
            positionlist[1],
            c=node_color,
            alpha=alpha,
            linewidth=node_linewidths,
            s=node_size,
            cmap=node_cmap,
            vmin=vmin,
            vmax=vmax,
            marker=node_shape,
            edgecolors=node_edge_color,
            zorder=2.5,
            label=node_title,
        )

        if node_title is not None:
            # Draw Legend graph for the specific nodes
            handles, labels = ax.get_legend_handles_labels()
            unique = [
                (h, l)
                for i, (h, l) in enumerate(zip(handles, labels))
                if l not in labels[:i]
            ]
            ax.legend(
                *zip(*unique),
                loc="upper center",
                fancybox=True,
                framealpha=1,
                shadow=True,
                borderpad=0.3,
                markerscale=0.5,
                markerfirst=True,
                ncol=3,
                bbox_to_anchor=(0.5, 1.15),
            )

    show = kwargs.get("show")  # check If the user call only the function of nodes
    if show is None and node_label is True:
        draw_labels(g, position, axis=axis, **kwargs)


def draw_edges(
    g,
    position,
    edge_color="black",
    edge_cmap=None,
    edge_linewidth=1.3,
    line_style="solid",
    arrow=False,
    arrow_size=1,
    arrow_style="-|>",
    arrow_color="black",
    arrow_line="-",
    arrow_head=20,
    edge_list=None,
    alpha=1,
    axis=False,
    edge_title=None,
    edge_label=False,
    connection_style=None,
    bbox=dict(boxstyle="round,pad=0.03", ec="white", fc="white"),
    ax=None,
    **kwargs
):
    """
          Parameters:
                    :param g: graph
                    :param position: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                    :type position: dictionary, optional
                    :param edge_color: Edge color
                    :type edge_color: color or array of colors (default='black')
                    :param edge_cmap: Colormap for mapping intensities of edges
                    :type edge_cmap: list, optional (default:edge_cmap=None | examle: edge_cmap =plt.cm.Greens(np.linspace(edge_vmin,edge_vmax,len(g.edges))))
                    :param edge_linewidth:Line width of edges
                    :type edge_linewidth:float, optional (default=1.3)
                    :param line_style:Edge line style (solid|dashed|dotted|dashdot)
                    :type line_style:string, optional (default='solid')
                    :param arrow:draw arrowheads
                    :type arrow:bool, optional (default=True)
                    :param arrow_size:size of arrow
                    :type arrow_size:int, optional (default=1)
                    :param arrow_style:choose the style of the arrowsheads.(Fancy|Simple|Wedge etc)
                    :type arrow_style:str, optional (default='-|>')
                    :param arrow_color: arrow color
                    :type arrow_color: color or array of colors (default='black')
                    :param arrow_line: Edge line style (solid|dashed|dotted|dashdot)
                    :type arrow_line:string, optional (default='solid')
                    :param arrow_head:size of arrowhead
                    :type arrow_head:int, optional (default=20)
                    :param edge_list:Draw only specified edges
                    :type edge_list:list, optional (default: edge_list=None)
                    :param alpha:edge transparency
                    :type alpha: float, optional (default=1.0)
                    :param axis:Draw the axes
                    :type axis:bool, optional (default=False)
                    :param edge_title:Label for graph legend
                    :type edge_title:list, optional  (default:None)
                    :param edge_label:draw labels on the edges.
                    :type edge_label: bool, optional (default=False)
                    :param connection_style:Pass the connection_style parameter to create curved arc of rounding radius rad
                    :type connection_style:str, optional (default=None | example: connection_style="arc3,rad=-0.3")
                    :param bbox: Matplotlib bbox,specify text box shape and colors.
                    :param ax: Draw the graph in the specified Matplotlib axes
                    :type ax:Matplotlib Axes object, optional
                    :param kwargs:See draw_jgrapht
                    :type kwargs:optional keywords
          """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import matplotlib as mpl
    except ImportError as e:
        raise ImportError("Matplotlib required for draw()") from e
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise
    if len(g.edges) != 0:
        if ax is None:
            ax = plt.gca()

        if axis is False:
            ax.set_axis_off()
        show = kwargs.get("show")  # check If the user call only the function of edges

        if edge_cmap is not None:  # if the user want color map for the edges
            plt.close()
            plt.rcParams["axes.prop_cycle"] = plt.cycler("color", edge_cmap)
            ax = plt.gca()
            if show is None:  # if  the user calls only this function
                draw_edges(
                    g,
                    position=position,
                    edge_label=edge_label,
                    edge_cmap=None,
                    edge_color="",
                    edge_linewidth=edge_linewidth,
                    line_style=line_style,
                    arrow=arrow,
                    arrow_size=arrow_size,
                    arrowstyle=arrow_style,
                    arrow_color=arrow_color,
                    edge_list=edge_list,
                    alpha=alpha,
                    axis=axis,
                    edge_title=edge_title,
                    connection_style=connection_style,
                    bbox=bbox,
                    ax=ax,
                    arrow_head=arrow_head,
                    arrow_line=arrow_line,
                    **kwargs,
                )
                return
            else:
                kwargs.pop("show")  # delete from kwargs the parameter show
                draw_jgrapht(
                    g,
                    position=position,
                    edge_cmap=None,
                    edge_color="",
                    edge_linewidth=edge_linewidth,
                    edge_list=edge_list,
                    line_style=line_style,
                    arrow=arrow,
                    arrow_size=arrow_size,
                    arrow_style=arrow_style,
                    arrow_color=arrow_color,
                    alpha=alpha,
                    axis=axis,
                    ax=ax,
                    edge_title=edge_title,
                    connection_style=connection_style,
                    edge_label=edge_label,
                    bbox=bbox,
                    arrow_head=arrow_head,
                    arrow_line=arrow_line,
                    **kwargs,
                )
                return
        k = 0  # counter of edges
        for e in g.edges:
            v1 = g.edge_source(e)
            v2 = g.edge_target(e)
            x1, y1 = position[v1]
            x2, y2 = position[v2]
            dy = y2 - y1
            dx = x2 - x1
            y1 = y1 + dy
            y2 = y2 - dy
            x1 = x1 + dx
            x2 = x2 - dx
            point1 = [x1, y1]
            point2 = [x2, y2]
            x_values = [point1[0], point2[0]]
            y_values = [point1[1], point2[1]]
            if edge_list is None:  # Draw all edges
                if arrow is True:
                    a = FancyArrowPatch(
                        (x2, y2),
                        (x1, y1),
                        arrowstyle=arrow_style,
                        shrinkA=9.5,
                        shrinkB=9.5,
                        mutation_scale=arrow_head,
                        alpha=alpha,
                        ls=arrow_line,
                        lw=arrow_size,
                        connectionstyle=connection_style,
                        color=arrow_color,
                        label=edge_title,
                    )
                    ax.add_patch(a)
                    ax.autoscale_view()
                else:
                    # Draw the edges
                    ax.plot(
                        x_values,
                        y_values,
                        edge_color,
                        alpha=alpha,
                        linewidth=edge_linewidth,
                        linestyle=line_style,
                        label=edge_title,
                    )

                if edge_title is not None:  # legend title for edges
                    handles, labels = ax.get_legend_handles_labels()
                    unique = [
                        (h, l)
                        for i, (h, l) in enumerate(zip(handles, labels))
                        if l not in labels[:i]
                    ]
                    ax.legend(
                        *zip(*unique),
                        loc="upper center",
                        fancybox=True,
                        framealpha=1,
                        shadow=True,
                        borderpad=0.3,
                        markerscale=0.5,
                        markerfirst=True,
                        ncol=3,
                        bbox_to_anchor=(0.5, 1.15),
                    )
            elif edge_list is not None:
                for l, edge in enumerate(edge_list):
                    if edge_list[l] == k:
                        if arrow is True:  # Draw specific arrows
                            a = FancyArrowPatch(
                                (x2, y2),
                                (x1, y1),
                                arrowstyle=arrow_style,
                                shrinkA=9.5,
                                shrinkB=9.5,
                                mutation_scale=arrow_head,
                                alpha=alpha,
                                ls=arrow_line,
                                lw=arrow_size,
                                connectionstyle=connection_style,
                                color=arrow_color,
                                label=edge_title,
                            )
                            ax.add_patch(a)
                            ax.autoscale_view()
                        else:
                            # Draw specific edges
                            ax.plot(
                                x_values,
                                y_values,
                                edge_color,
                                alpha=alpha,
                                linewidth=edge_linewidth,
                                linestyle=line_style,
                                label=edge_title,
                            )

                        if (
                            edge_title is not None
                        ):  # legend title for the specific edges
                            handles, labels = ax.get_legend_handles_labels()
                            unique = [
                                (h, l)
                                for i, (h, l) in enumerate(zip(handles, labels))
                                if l not in labels[:i]
                            ]
                            ax.legend(
                                *zip(*unique),
                                loc="upper center",
                                fancybox=True,
                                framealpha=1,
                                shadow=True,
                                borderpad=0.3,
                                markerscale=0.5,
                                markerfirst=True,
                                ncol=3,
                                bbox_to_anchor=(0.5, 1.15),
                            )
            k = k + 1
        if show is None and edge_label is True:
            draw_edge_labels(g, position, axis=axis, **kwargs)


def draw_labels(
    g,
    position,
    node_fontsize=12,
    node_font_color="black",
    node_font_weight="normal",
    node_font_family="sans-serif",
    horizontalalignment="center",
    verticalalignment="center",
    alpha=1,
    axis=False,
    bbox=dict(boxstyle="round,pad=0.03", ec="white", fc="white"),
    ax=None,
    node_names=None,
    **kwargs
):
    """
             Parameters:
                            :param g: graph
                            :param position: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                            :type position: dictionary, optional
                            :param node_fontsize: Font size for text labels
                            :type node_fontsize:int, optional (default=12)
                            :param node_font_color: Font color string
                            :type node_font_color:string, optional (default='black')
                            :param node_font_weight: Font weight ( 'normal' | 'bold' | 'heavy' | 'light' | 'ultralight')
                            :type node_font_weight:string, optional (default='normal')
                            :param node_font_family: Font family ('cursive', 'fantasy', 'monospace', 'sans', 'sans serif', 'sans-serif', 'serif')
                            :type node_font_family: string, optional (default='sans-serif')
                            :param verticalalignment: Vertical alignment (default='center')
                            :type verticalalignment: {'center', 'top', 'bottom', 'baseline', 'center_baseline'}
                            :param horizontalalignment:Horizontal alignment (default='center')
                            :type horizontalalignment: {'center', 'right', 'left'}
                            :param alpha:edge transparency
                            :type alpha: float, optional (default=1.0)
                            :param axis:Draw the axes
                            :type axis:bool, optional (default=False)
                            :param ax: Draw the graph in the specified Matplotlib axes
                            :type ax:Matplotlib Axes object, optional
                            :param node_names: label names for nodes
                            :type node_names: list, optional
                            :param kwargs:See draw_jgrapht
                            :type kwargs:optional keywords
          """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib required for draw()") from e
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if not axis:
        ax.set_axis_off()

    if node_names is None:
        for i, vertex in enumerate(g.vertices):
            # Draw Labels of nodes
            x, y = position[i]
            ax.text(
                x,
                y,
                i,
                fontsize=node_fontsize,
                horizontalalignment=horizontalalignment,
                verticalalignment=verticalalignment,
                alpha=alpha,
                color=node_font_color,
                weight=node_font_weight,
                family=node_font_family,
                transform=ax.transData,
            )
            ax.plot(
                x, y
            )  # It helps when the user wants to see only labels and nothing else
    else:
        for i, vertex in enumerate(node_names):
            # Draw the labels that user gave
            x, y = position[i]
            ax.text(
                x,
                y,
                node_names[i],
                fontsize=node_fontsize,
                horizontalalignment=horizontalalignment,
                verticalalignment=verticalalignment,
                alpha=alpha,
                color=node_font_color,
                weight=node_font_weight,
                family=node_font_family,
                transform=ax.transData,
            )
            ax.plot(
                x, y
            )  # It helps when the user wants to see only labels and nothing else


def draw_edge_labels(
    g,
    position,
    horizontalalignment="center",
    verticalalignment="center",
    edge_fontsize=12,
    edge_font_color="black",
    edge_font_weight="normal",
    edge_font_family="sans-serif",
    alpha=1,
    axis=False,
    bbox=dict(boxstyle="round,pad=0.03", ec="white", fc="white"),
    ax=None,
    edge_names=None,
    draw_edge_weights=False,
    **kwargs
):
    """
             Parameters:
                            :param g: graph
                            :param position: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                            :type position: dictionary, optional
                            :param edge_fontsize: Font size for text labels
                            :type edge_fontsize:int, optional (default=12)
                            :param edge_font_color: Font color string
                            :type edge_font_color:string, optional (default='black')
                            :param edge_font_weight: Font weight ( 'normal' | 'bold' | 'heavy' | 'light' | 'ultralight')
                            :type edge_font_weight:string, optional (default='normal')
                            :param edge_font_family: Font family ('cursive', 'fantasy', 'monospace', 'sans', 'sans serif', 'sans-serif', 'serif')
                            :type  edge_font_family: string, optional (default='sans-serif')
                            :param verticalalignment: Vertical alignment (default='center')
                            :type verticalalignment: {'center', 'top', 'bottom', 'baseline', 'center_baseline'}
                            :param horizontalalignment:Horizontal alignment (default='center')
                            :type horizontalalignment: {'center', 'right', 'left'}
                            :param alpha:edge transparency
                            :type alpha: float, optional (default=1.0)
                            :param axis:Draw the axes
                            :type axis:bool, optional (default=False)
                            :param bbox: Matplotlib bbox,specify text box shape and colors.
                            :param ax: Draw the graph in the specified Matplotlib axes
                            :type ax:Matplotlib Axes object, optional
                            :param edge_names: label names for edges
                            :type edge_names: list, optional
                            :param draw_edge_weights:weights of edges
                            :type draw_edge_weights:bool, optional (default=False)
                            :param kwargs:See draw_jgrapht
                            :type kwargs:optional keywords
          """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib required for draw()") from e
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise
    if len(g.edges) != 0:
        if ax is None:
            ax = plt.gca()

        if not axis:
            ax.set_axis_off()
        if edge_names is None:
            if draw_edge_weights is True:
                # Draw Labels of edges
                for e in g.edges:
                    v1 = g.edge_source(e)
                    v2 = g.edge_target(e)
                    x1, y1 = position[v1]
                    x2, y2 = position[v2]
                    ax.text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        g.get_edge_weight(e),
                        fontsize=edge_fontsize,
                        horizontalalignment=horizontalalignment,
                        verticalalignment=verticalalignment,
                        alpha=alpha,
                        color=edge_font_color,
                        weight=edge_font_weight,
                        family=edge_font_family,
                        bbox=bbox,
                        zorder=2,
                        transform=ax.transData,
                    )
                    ax.plot(
                        (x1 + x2) / 2, (y1 + y2) / 2
                    )  # It helps when the user wants to see only labels and nothing else
            else:
                # Draw Labels of edges
                for e in g.edges:
                    v1 = g.edge_source(e)
                    v2 = g.edge_target(e)
                    x1, y1 = position[v1]
                    x2, y2 = position[v2]
                    ax.text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        e,
                        fontsize=edge_fontsize,
                        horizontalalignment=horizontalalignment,
                        verticalalignment=verticalalignment,
                        alpha=alpha,
                        color=edge_font_color,
                        weight=edge_font_weight,
                        family=edge_font_family,
                        bbox=bbox,
                        zorder=2,
                        transform=ax.transData,
                    )
                    ax.plot(
                        (x1 + x2) / 2, (y1 + y2) / 2
                    )  # It helps when the user wants to see only labels and nothing else

        else:
            for e, edges in enumerate(edge_names):
                v1 = g.edge_source(e)
                v2 = g.edge_target(e)
                x1, y1 = position[v1]
                x2, y2 = position[v2]
                # Draw the labels that user gave
                x, y = position[e]
                ax.text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    edge_names[e],
                    fontsize=edge_fontsize,
                    horizontalalignment=horizontalalignment,
                    verticalalignment=verticalalignment,
                    alpha=alpha,
                    color=edge_font_color,
                    weight=edge_font_weight,
                    family=edge_font_family,
                    transform=ax.transData,
                    bbox=bbox,
                    zorder=2,
                )
                ax.plot(
                    (x1 + x2) / 2, (y1 + y2) / 2
                )  # It helps when the user wants to see only labels and nothing else


def layout(g, pos_layout=None, area=None, **kwargs):
    """
                Parameters:
                    :param g: the graph to draw
                    :param pos_layout: circular_layout|random_layout|fruchterman_reingold_layout|fruchterman_reingold_indexed_layout
                    :type pos_layout: dictionary, optional
                    :param area: the two dimensional area as a tuple (minx, miny, width, height)
                    :param kwargs:See draw_jgrapht
                    :type kwargs:optional keywords
                     """
    position = []
    if area is None:
        area = (0, 0, 10, 10)
    if pos_layout is None or pos_layout == "circular_layout":
        model = jgrapht.algorithms.drawing.circular_layout_2d(g, area, radius=5)
    elif pos_layout == "random_layout":
        model = jgrapht.algorithms.drawing.random_layout_2d(g, area)
    elif pos_layout == "fruchterman_reingold_layout":
        model = jgrapht.algorithms.drawing.fruchterman_reingold_layout_2d(g, area)
    elif pos_layout == "fruchterman_reingold_indexed_layout":
        model = jgrapht.algorithms.drawing.fruchterman_reingold_layout_2d(g, area)

    for i, vertex in enumerate(g.vertices):
        x, y = model.get_vertex_location(i)
        position.append((x, y))

    return position


def circular(g, **kwargs):
    """
               Parameters:
                    :param g: graph
                    :param kwargs:See draw_jgrapht,draw_nodes,draw_edges,draw_Lables,draw_edge_labels
                    :type kwargs:optional keywords
          """
    draw_jgrapht(g, layout(g, pos_layout="circular_layout"), **kwargs)


def random(g, **kwargs):
    """
               Parameters:
                     :param g: graph
                     :param kwargs:See draw_jgrapht,draw_nodes,draw_edges,draw_Lables,draw_edge_labels
                     :type kwargs:optional keywords
          """
    draw_jgrapht(g, layout(g, pos_layout="random_layout"), **kwargs)


def fruchterman_reingold(g, **kwargs):
    """
               Parameters:
                      :param g: graph
                      :param kwargs:See draw_jgrapht,draw_nodes,draw_edges,draw_Lables,draw_edge_labels
                      :type kwargs:optional keywords
          """
    draw_jgrapht(g, layout(g, pos_layout="fruchterman_reingold_layout"), **kwargs)


def fruchterman_reingold_indexed(g, **kwargs):
    """
               Parameters:
                    :param g: graph
                    :param kwargs:See draw_jgrapht,draw_nodes,draw_edges,draw_Lables,draw_edge_labels
                    :type kwargs:optional keywords
          """
    draw_jgrapht(
        g, layout(g, pos_layout="fruchterman_reingold_indexed_layout"), **kwargs
    )
