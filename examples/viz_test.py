import numpy as np
import matplotlib.pyplot as plt

try:
    from pyxdsm.XDSM import XDSM,  OPT, SOLVER, FUNC
except ImportError:
    print("pyXDSM package not found. Please install it using `pip install pyXDSM`.")
    

def dict_to_xdsm(data, filename='xdsm', show_browser=True):
    """
    Convert a dictionary to an XDSM diagram.

    Parameters
    ----------
    data : dict
        Dictionary representing the XDSM diagram.
        It should have the following structure:
        {
            'nodes': {
                'node1': {'shape': 'box', 'label': 'Node 1'},
                'node2': {'shape': 'ellipse', 'label': 'Node 2'},
                ...
            },
            'edges': [
                ('node1', 'node2', {'label': 'Edge Label'}),
                ...
            ]
        }
    filename : str, optional
        Name of the output file (without extension).
    show_browser : bool, optional
        If True, show the XDSM diagram in the default web browser.

    Returns
    -------
    None
    """
    

    # Create the XDSM object
    xdsm = XDSM()

    # Add the nodes
    for name, props in data['nodes'].items():
        xdsm.add_system(name, **props)

    # Add the edges
    for src, tgt, props in data['edges']:
        xdsm.connect(src, tgt, **props)

    # Write the XDSM file
    xdsm.write(filename, True)

    # Show the XDSM diagram in the browser
    # if show_browser:
    #     xdsm.display()


data = {
    'nodes': {
        'node1': {'style': OPT, 'label': 'Node 1'},
        'node2': {'style': SOLVER, 'label': 'Node 2'},
    },
    'edges': [
        ('node1', 'node2', {'label': 'Edge Label'}),
    ]
}

dict_to_xdsm(data=data)

# from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC, LEFT

# # Change `use_sfmath` to False to use computer modern
# x = XDSM(use_sfmath=True)

# x.add_system("opt", OPT, r"\text{Optimizer}")
# x.add_system("solver", SOLVER, r"\text{Newton}")
# x.add_system("D1", FUNC, "D_1")
# x.add_system("D2", FUNC, "D_2")
# x.add_system("F", FUNC, "F")
# x.add_system("G", FUNC, "G")

# x.connect("opt", "D1", "x, z")
# x.connect("opt", "D2", "z")
# x.connect("opt", "F", "x, z")
# x.connect("solver", "D1", "y_2")
# x.connect("solver", "D2", "y_1")
# x.connect("D1", "solver", r"\mathcal{R}(y_1)")
# x.connect("solver", "F", "y_1, y_2")
# x.connect("D2", "solver", r"\mathcal{R}(y_2)")
# x.connect("solver", "G", "y_1, y_2")

# x.connect("F", "opt", "f")
# x.connect("G", "opt", "g")

# x.add_output("opt", "x^*, z^*", side=LEFT)
# x.add_output("D1", "y_1^*", side=LEFT)
# x.add_output("D2", "y_2^*", side=LEFT)
# x.add_output("F", "f^*", side=LEFT)
# x.add_output("G", "g^*", side=LEFT)
# x.write("mdf")


# def dict_to_xdsm(d, output_file=None):
#     """
#     Convert a dictionary to a XDSM diagram and optionally save it to a file.
    
#     Args:
#         d (dict): The dictionary to convert to a XDSM.
#         output_file (str): The name of the file to save the XDSM to. Defaults to None.
        
#     Returns:
#         str: The XDSM diagram as a string.
#     """
    
#     # Import the necessary libraries
#     from pyxdsm.XDSM import XDSM
    
#     # Create the XDSM object
#     xdsm = XDSM()
    
#     # Loop through the dictionary and add each component
#     for comp_name, comp_dict in d.items():
#         if "comp" in comp_dict:
#             xdsm.add_system(comp_name, comp_dict["comp"])
#         elif "group" in comp_dict:
#             xdsm.add_process(comp_name, comp_dict["group"])
    
#     # Loop through the dictionary again and add each connection
#     for from_name, from_dict in d.items():
#         for to_name, to_dict in from_dict.get("connect", {}).items():
#             xdsm.add_input_output(from_name, to_name, from_dict["var"], to_dict["var"])
    
#     # Generate the XDSM diagram
#     xdsm.write(output_format="tex")
    
#     # If an output file was specified, save the XDSM diagram to the file
#     if output_file:
#         xdsm.write(output_format="pdf", output_name=output_file)
    
#     # Return the XDSM diagram as a string
#     return xdsm.tex

# from collections import defaultdict
# from graphviz import Digraph

# def dict_to_xdsm(data, filename='xdsm'):
#     nodes = defaultdict(set)
#     for key in data:
#         for item in data[key]:
#             nodes[key].add(item)
#             nodes[item]  # ensure the item is in the nodes dict even if it has no connections

#     # create graph
#     dot = Digraph(comment='XDSM Diagram', filename=filename, engine='dot')

#     # add nodes
#     for node in nodes:
#         dot.node(node, node)

#     # add edges
#     for key in data:
#         for item in data[key]:
#             dot.edge(key, item)

#     # render graph
#     dot.render(view=True)

# data = {
#     'A': ['B', 'C'],
#     'B': ['A','D'],
#     'C': ['D'],
#     'D': ['E'],
#     'E': []
# }

# dict_to_xdsm(data, filename='my_xdsm')


# import numpy as np
# import matplotlib.pyplot as plt

# def create_xdsm(diagram_dict):
#     box_width = 0.3
#     box_height = 0.2
#     box_sep = 0.1
#     fig = plt.figure(figsize=(10, 8))
#     ax = fig.add_subplot(1, 1, 1)
#     ax.set_axis_off()
#     x_pos = {}
#     y_pos = {}
#     i = 0
#     for node in diagram_dict['nodes']:
#         x_pos[node] = 0
#         y_pos[node] = i
#         ax.text(x_pos[node] - 0.5 * box_width, y_pos[node] + 0.5 * box_height, node, fontsize=12)
#         i += 1
#     num_nodes = i
#     for i, group in enumerate(diagram_dict['edges']):
#         for j, conn in enumerate(group):
#             from_node = conn[0]
#             to_node = conn[1]
#             arrow_style = '-|>' if conn[2] == 'out' else '<|-'
#             x_start = x_pos[from_node] + 0.5 * box_width
#             y_start = y_pos[from_node] - 0.5 * box_height
#             x_end = x_pos[to_node] - 0.5 * box_width
#             y_end = y_pos[to_node] - 0.5 * box_height
#             ax.arrow(x_start, y_start, x_end - x_start, y_end - y_start, lw=1, head_width=0.05, head_length=0.05,
#                      length_includes_head=True, shape=arrow_style, color='k')
#     plt.ylim(-num_nodes * (box_height + box_sep), box_height)
#     plt.xlim(-0.5, max(x_pos.values()) + 0.5)
#     plt.show()


# d = { 'nodes' : {
#     'A':  ['B', 'C'],
#     'B': ['D'],
#     'C': ['D', 'E'],
#     'D': ['F'],
#     'E': ['F'],
#     'F': [],
#     },
# }

# create_xdsm(d)

# import graphviz

# def dict_to_xdsm(d, filename):
#     dot = graphviz.Digraph()
    
#     # Add all the nodes
#     for node in d.keys():
#         dot.node(node)
    
#     # Add all the edges
#     for source, targets in d.items():
#         for target in targets:
#             dot.edge(source, target)
    
#     # Render the graph and save it to a file
#     dot.render(filename, format='png')

# d = {
#     'A': ['B', 'C'],
#     'B': ['D'],
#     'C': ['D', 'E'],
#     'D': ['F'],
#     'E': ['F'],
#     'F': []
# }

# import os
# file_name= os.getcwd()+'/' + 'example.png'
# dict_to_xdsm(d, file_name)

