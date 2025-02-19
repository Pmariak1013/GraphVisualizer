import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import colorchooser
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

class GraphVisualizer:
    def __init__(self, master):
        self.master = master
        self.colors = {}
        master.title("Graph Algorithm Visualizer")
        master.geometry("800x600")

        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_columnconfigure(0, weight=1)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_xticks([])  # Remove x-axis ticks
        self.ax.set_yticks([])  # Remove y-axis ticks
        self.ax.spines['top'].set_visible(False)  # Hide top border
        self.ax.spines['right'].set_visible(False)  # Hide right border
        self.ax.spines['left'].set_visible(False)  # Hide left border
        self.ax.spines['bottom'].set_visible(False) 
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()

        self.canvas_widget.grid(row=0, column=0, sticky="nsew", pady=10)

        self.load_graph()
        if not self.graph:
            self.graph = nx.Graph()

        frame = tk.Frame(master, padx=10, pady=10)
        frame.grid(row=1, column=0, sticky="ew", pady=10)

        buttons = [
            ("Add Node", self.add_node),
            ("Add Edge", lambda: self.edge_window(0)),
            ("Remove Node", self.remove_node_window),
            ("Remove Edge", lambda: self.edge_window(1)),
            ("Clear", self.clear_graph),
            ("Save", self.save_graph),
            ("Save As", self.save_as),
            ("Load", self.open_file_explorer),
            ("Delete Graph", self.delete_graph),
            ("Choose Node Color",self.color_window)
        ]

        for i, (text, command) in enumerate(buttons):
            button = tk.Button(frame, text=text, command=command)
            button.grid(row=0, column=i, padx=5)

        self.master.bind("<Configure>", self.resize_plot)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.master.quit()
        self.master.destroy() 

    def add_node(self):
        node_name = simpledialog.askstring("Node Input", "Enter node name:")
        if node_name:
            self.graph.add_node(node_name)
            self.draw_graph()

    def edge_window(self, action):
        actionString = "Add" if action == 0 else "Remove"
        edge_selector = tk.Toplevel(self.master)
        edge_selector.title(f"Select Edge to {actionString}")
        nodes = list(self.graph.nodes)

        label1 = tk.Label(edge_selector, text="Select node 1:")
        label1.pack(pady=10)
        node_selector1 = ttk.Combobox(edge_selector, values=nodes)
        node_selector1.pack(pady=10)

        label2 = tk.Label(edge_selector, text="Select node 2:")
        label2.pack(pady=10)
        node_selector2 = ttk.Combobox(edge_selector, values=nodes)
        node_selector2.pack(pady=10)

        edge_selector.geometry("250x250")
        add_edge_button = tk.Button(edge_selector, text=actionString, 
                                    command=lambda: (self.add_edge(node_selector1, node_selector2, edge_selector) if action==0
                                    else self.remove_edge(node_selector1, node_selector2,edge_selector)))
        add_edge_button.pack(pady=10)

    def add_edge(self,node1,node2, window):
        node1_name, node2_name = node1.get(), node2.get()
        if node1_name in self.graph and node2_name in self.graph:
            self.graph.add_edge(node1_name, node2_name)
            self.draw_graph()
        window.destroy()
        print(f"Added edge between {node1_name} and {node2_name}")

    def remove_node_window(self):
        remove_window = tk.Toplevel(self.master)
        remove_window.title("Select Node to Remove")
        node_names = list(self.graph.nodes)

        label = tk.Label(remove_window, text="Select a node to remove:")
        label.pack(pady=10)
        node_selector = ttk.Combobox(remove_window, values=node_names)
        node_selector.pack(pady=10)

        remove_window.geometry("250x150")
        remove_button = tk.Button(remove_window, text="Remove Node", command=lambda:self.remove_node(node_selector, remove_window))
        remove_button.pack(pady=10)

    def remove_node(self,node,window):
        node_name = node.get()
        if node_name in self.graph:
            self.graph.remove_node(node_name)
            for node in self.graph.nodes:
                if (node_name, node) in self.graph.edges:
                    self.graph.remove_edge(node_name,node)
            self.draw_graph()
        window.destroy()
        print(f"Removed {node_name}")
    
    def remove_edge(self,node1,node2,window):
        node1_name, node2_name = node1.get(),node2.get()
        if node1_name and node2_name and (node1_name, node2_name) in self.graph.edges:
            self.graph.remove_edge(node1_name, node2_name)
            self.draw_graph()
        window.destroy()
        print(f"Removed edge between {node1_name} and {node2_name}")

    def color_window(self):
        color = tk.Toplevel(self.master)
        color.title("Node Color Chooser")
        node_names = list(self.graph.nodes)

        label = tk.Label(color, text="Select a node to color:")
        label.pack(pady=10)
        node_selector = ttk.Combobox(color, values=node_names)
        node_selector.pack(pady=10)

        color.geometry("250x150")
        color_button = tk.Button(color, text="Color", command=lambda:self.color_chooser(node_selector.get(),color))
        color_button.pack(pady=10)

    def color_chooser(self,node,window):
        if node:
            color = colorchooser.askcolor()[1]
            if color:
                self.colors[node] = color
                self.draw_graph()
        window.destroy()

    def clear_graph(self):
        self.graph.clear()
        self.draw_graph()
        print("Graph cleared")

    def draw_graph(self):
        self.ax.clear() 
        pos = nx.spring_layout(self.graph)
        node_colors = [self.colors[node] if node in self.colors.keys() else "lightblue" for node in self.graph.nodes]
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, ax=self.ax)
        nx.draw_networkx_edges(self.graph, pos, ax=self.ax, edge_color='black', width=1)    
        nx.draw_networkx_labels(self.graph, pos, ax=self.ax)
        self.canvas.draw()
        print(self.graph)
        print(self.colors)
    
    def save_graph(self,filename="graph.json"):
        data = {
            "nodes": [str(node) for node in self.graph.nodes],
            "edges": [(str(u), str(v)) for u, v, in self.graph.edges],
            "colors": [(str(key),self.colors[key]) for key in self.colors.keys()]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Graph saved as {filename}")

    def save_as(self):
        filename = filedialog.asksaveasfilename(title="Save Graph As", defaultextension=".json")
        if filename:
            self.save_graph(filename)
            print("Graph saved as", filename)
        else:
            print("No filename provided")
    
    def load_graph(self, filename="graph.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            self.graph = nx.Graph()
            self.graph.add_nodes_from(data["nodes"])
            self.graph.add_edges_from(data["edges"])
            if "colors" in data:
                self.colors = {item[0]:item[1] for item in data["colors"]}

            print(self.graph)
            self.draw_graph()
            print(f"Graph loaded from {filename}")

        except FileNotFoundError:
            print(f"No file found at {filename}")
    
    def delete_graph(self, filename="graph.json"):
        self.colors.clear()
        empty_data = {
            "nodes": [],
            "edges": [],
            "colors": []
            }
        
        with open(filename, "w") as f:
            json.dump(empty_data, f)
        print(f"Graph file '{filename}' deleted.")

    def open_file_explorer(self):
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            self.load_graph(file_path)
            print("Selected File:", file_path)

    def resize_plot(self, event):
        self.figure.set_size_inches(self.master.winfo_width() / 100, 4)  # Adjust width
        self.canvas.draw()

def main():
    root = tk.Tk()
    visualizer = GraphVisualizer(root)
    root.mainloop()

if __name__=="__main__":
    main()