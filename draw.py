#!/usr/bin/env python3
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

NODE_EDGE_COLOR = "black"
NODE_FILL_COLOR = "white"
NODE_LABEL_COLOR = "blue"
NODE_TEXT_COLOR = "white"
PROPERTY_LABEL_COLOR = "grey"
PROPERTY_TEXT_COLOR = "white"
RELATIONSHIP_LINE_COLOR = "black"
RELATIONSHIP_TEXT_COLOR = "black"


def load_graph(json_filename):
    with open(json_filename, "r") as f:
        data = json.load(f)
    return data


def build_graph(data):
    G = nx.DiGraph()
    pos = {}

    for node in data["nodes"]:
        node_id = node["id"]
        x = node["position"]["x"]
        y = node["position"]["y"]
        pos[node_id] = (x, y)

        if node.get("labels"):
            label_text = "\n".join(node["labels"])
        elif node.get("caption"):
            label_text = node["caption"]
        else:
            label_text = node_id

        properties = node.get("properties", {})
        G.add_node(node_id, label=label_text, properties=properties)

    for rel in data["relationships"]:
        from_id = rel.get("fromId")
        to_id = rel.get("toId")
        G.add_edge(
            from_id, to_id, type=rel.get("type"), properties=rel.get("properties")
        )

    return G, pos


def draw_graph(G, pos, output_filename="graph.svg"):
    xs = [coord[0] for coord in pos.values()]
    ys = [coord[1] for coord in pos.values()]
    margin = 50
    x_min, x_max = min(xs) - margin, max(xs) + margin
    y_min, y_max = min(ys) - margin, max(ys) + margin

    fig_width = (x_max - x_min) / 100
    fig_height = (y_max - y_min) / 100
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=1500,
        node_color=NODE_FILL_COLOR,
        edgecolors=NODE_EDGE_COLOR,
        ax=ax,
    )

    labels = nx.get_node_attributes(G, "label")
    for node, (x, y) in pos.items():
        ax.text(
            x,
            y,
            labels[node],
            fontsize=8,
            color=NODE_TEXT_COLOR,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc=NODE_LABEL_COLOR,
                ec=NODE_LABEL_COLOR,
                alpha=1.0,
            ),
        )

    for node, attr in G.nodes(data=True):
        properties = attr.get("properties", {})
        if properties:
            prop_text = "\n".join(f"{k}: {v}" for k, v in properties.items())
            x, y = pos[node]
            ax.text(
                x,
                y + 50,
                prop_text,
                fontsize=7,
                color=PROPERTY_TEXT_COLOR,
                verticalalignment="top",
                horizontalalignment="left",
                bbox={
                    "facecolor": PROPERTY_LABEL_COLOR,
                    "edgecolor": PROPERTY_LABEL_COLOR,
                    "alpha": 1.0,
                    "pad": 2,
                    "boxstyle": "round,pad=0.3",
                },
            )

    for edge in G.edges():
        x1, y1 = pos[edge[0]]
        x2, y2 = pos[edge[1]]
        dx, dy = x2 - x1, y2 - y1

        shrink_factor = 30
        distance = (dx**2 + dy**2) ** 0.5
        if distance > 0:
            x1 += (dx / distance) * shrink_factor
            y1 += (dy / distance) * shrink_factor
            x2 -= (dx / distance) * shrink_factor
            y2 -= (dy / distance) * shrink_factor

        arrow = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            color=RELATIONSHIP_LINE_COLOR,
            mutation_scale=15,
            lw=1,
        )
        ax.add_patch(arrow)

    edge_labels = nx.get_edge_attributes(G, "type")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_color=RELATIONSHIP_TEXT_COLOR,
        font_size=8,
        ax=ax,
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.invert_yaxis()

    ax.axis("off")

    plt.savefig(output_filename, format="svg", dpi=300, bbox_inches="tight")
    print(f"Graph saved as {output_filename}")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <input_json_file> <output_svg_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    output_filename = sys.argv[2]
    data = load_graph(json_file)
    G, pos = build_graph(data)
    draw_graph(G, pos, output_filename=output_filename)


if __name__ == "__main__":
    main()
