import pandas as pd 
import networkx as nx 
from os.path import join 
import numpy as np 
import json 

DATA_BASE = 'data'
STATS_BASE = 'statistics'

def load_csv(from_file=None): 
    with open(from_file) as fp: 
        return pd.read_csv(fp)


def build_graph(triples_df): 
    KG = nx.DiGraph() 
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
        return e.__repr__()  # There are infinite paths if the graph is not strongly connected


def mean(components, key=None): 
    sum_key = sum([len(component) for component in components])
    mean_size = sum_key / len(components)

    return list(sorted(components, key=lambda x: abs(len(x) - mean_size)))[0]



if __name__ == "__main__": 
    triples_raw = load_csv(join(DATA_BASE, 'dbpedia_triples.csv'))
    KG = build_graph(triples_raw)

    node_degrees = [degree for (node, degree) in KG.degree()]
    weakly_connected_components = list(nx.weakly_connected_components(KG))
    strongly_connected_components = list(nx.strongly_connected_components(KG))
    
    with open(join(STATS_BASE, 'dbpedia_statistics.json'), 'w') as fp: 
        json.dump({
            'database' : 'DBPedia',
            'query_selection' : 'MATCH (h:MovieRelated)-[r]->(t:MovieRelated)',
            'n_nodes' : len(KG.nodes()),
            'n_edges' : len(KG.edges()),
            'density' : nx.density(KG),
            'node_degrees' : {
                'min' : int(np.min(node_degrees)),
                'max' : int(np.max(node_degrees)),
                'avg' : int(np.average(node_degrees)),
                'median' : int(np.median(node_degrees))
            },
            'weakly_connected_components' : {
                'n_components' : len(weakly_connected_components),
                'largest' : {
                    'n_nodes' : len(max(weakly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, max(weakly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(max(weakly_connected_components, key=len), nx.edges(KG, max(weakly_connected_components, key=len))))
                },
                'average' : {
                    'n_nodes' : len(mean(weakly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, mean(weakly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(mean(weakly_connected_components, key=len), nx.edges(KG, mean(weakly_connected_components, key=len))))
                },
                'smallest' : {
                    'n_nodes' : len(min(weakly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, min(weakly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(min(weakly_connected_components, key=len), nx.edges(KG, min(weakly_connected_components, key=len))))
                }
            },
            'strongly_connected_components' : {
                'n_components' : len(strongly_connected_components),
                'largest' : {
                    'n_nodes' : len(max(strongly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, max(strongly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(max(strongly_connected_components, key=len), nx.edges(KG, max(strongly_connected_components, key=len))))
                },
                'average' : {
                    'n_nodes' : len(mean(strongly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, mean(strongly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(mean(strongly_connected_components, key=len), nx.edges(KG, mean(strongly_connected_components, key=len))))
                },
                'smallest' : {
                    'n_nodes' : len(min(strongly_connected_components, key=len)),
                    'n_edges' : len(nx.edges(KG, min(strongly_connected_components, key=len))),
                    'diameter' : diameter(build_sub_graph(min(strongly_connected_components, key=len), nx.edges(KG, min(strongly_connected_components, key=len))))
                }
            }
        }, fp, indent=True)
    

    