import pandas as pd 
import networkx as nx 
from os.path import join 
import numpy as np 
import json 

DATA_BASE = 'data'
STATS_BASE = 'statistics'
GRAPH = 'Wikidata'
TRIPLES = join(DATA_BASE, 'wikidata_triples.csv')

def load_csv(from_file=None): 
    with open(from_file) as fp: 
        return pd.read_csv(fp)


def build_graph(triples_df, directed=True): 
    KG = nx.DiGraph() if directed else nx.Graph() 
    for triple in triples_df.iterrows(): 
        triple = triple[-1]
        head = triple['head']
        relation = triple['relation']
        tail = triple['tail']

        KG.add_node(head)
        KG.add_node(tail)
        KG.add_edge(head, tail, type=relation)
    
    return KG 


def build_sub_graph(nodes, edges): 
    sub_KG = nx.DiGraph()
    for node in nodes: 
        sub_KG.add_node(node)

    for edge in edges: 
        sub_KG.add_edge(*edge)
    
    return sub_KG


def diameter(G): 
    try: 
        return nx.diameter(G)
    except nx.exception.NetworkXError as e: 
        return e.args  # There are infinite paths if the graph is not strongly connected


def mean(components, key=None): 
    sum_key = sum([len(component) for component in components])
    mean_size = sum_key / len(components)

    return list(sorted(components, key=lambda x: abs(len(x) - mean_size)))[0]


def get_components_statistics(components): 
    return {
        'n_components' : len(components),
        'largest' : {
            'n_nodes' : len(max(components, key=len)),
            'n_edges' : len(nx.edges(KG, max(components, key=len))),
            'diameter' : diameter(build_sub_graph(max(components, key=len), nx.edges(KG, max(components, key=len))))
        },
        'average' : {
            'n_nodes' : len(mean(components, key=len)),
            'n_edges' : len(nx.edges(KG, mean(components, key=len))),
            'diameter' : diameter(build_sub_graph(mean(components, key=len), nx.edges(KG, mean(components, key=len))))
        },
        'smallest' : {
            'n_nodes' : len(min(components, key=len)),
            'n_edges' : len(nx.edges(KG, min(components, key=len))),
            'diameter' : diameter(build_sub_graph(min(components, key=len), nx.edges(KG, min(components, key=len))))
        }
    }

def get_statistics(KG): 
    node_degrees = [degree for (node, degree) in KG.degree()]
    if isinstance(KG, nx.DiGraph): 
        weakly_connected_components = list(nx.weakly_connected_components(KG))
        strongly_connected_components = list(nx.strongly_connected_components(KG))
    else: 
        connected_components = list(nx.connected_components(KG))
    
    return {
        'database' : GRAPH,
        'directed' : isinstance(KG, nx.DiGraph),
        'n_nodes' : len(KG.nodes()),
        'n_edges' : len(KG.edges()),
        'density' : nx.density(KG),
        'node_degrees' : {
            'min' : int(np.min(node_degrees)),
            'max' : int(np.max(node_degrees)),
            'avg' : int(np.average(node_degrees)),
            'median' : int(np.median(node_degrees))
        },
        'components' : {
            'weakly_connected_components' : get_components_statistics(weakly_connected_components),
            'strongly_connected_components' : get_components_statistics(strongly_connected_components)
        } if isinstance(KG, nx.DiGraph) else {
            'connected_components' : get_components_statistics(connected_components)
        }
    }


if __name__ == "__main__": 
    triples_raw = load_csv(TRIPLES)

    for directed in [True, False]: 
        KG = build_graph(triples_raw, directed=directed)
        with open(join(STATS_BASE, f'{GRAPH.lower()}_statistics_{"directed" if directed else "undirected"}.json'), 'w') as fp: 
            json.dump(get_statistics(KG), fp, indent=True)
    

    