import json
from graphviz import Digraph

# JSON string representing the FSM
fsm_json = """
{
    "name": "prosumer",
    "initial_state": "start",
    "states": [
        "start",
        "rain",
        "sun"
    ],
    "transitions": [
        {
            "source": "start",
            "target": "rain",
            "condition": "x>5"
        },
        {
            "source": "rain",
            "target": "sun",
            "condition": "y>3"
        },
        {
            "source": "sun",
            "target": "rain",
            "condition": "z<2"
        }
    ]
}
"""

# Parse the JSON string
fsm = json.loads(fsm_json)

# Create a directed graph
dot = Digraph(name=fsm["name"])

# Set graph attributes
dot.attr(size='8,8')  # Set the size of the graph (width,height)
dot.attr('node', margin='0.2,0.2')  # Increase margin around the nodes
dot.attr('edge', fontsize='12')  # Increase the font size for edges

# Add states to the graph
for state in fsm["states"]:
    dot.node(state)

# Add transitions to the graph
for transition in fsm["transitions"]:
    dot.edge(transition["source"], transition["target"], label=transition["condition"], minlen='2')




# Save and render the graph
dot.render('fsm_graph', format='png', cleanup=True)
print("FSM graph saved as 'fsm_graph.png'")
