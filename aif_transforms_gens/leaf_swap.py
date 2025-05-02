import random
from copy import deepcopy

class LeafsSwapsAIF:
    def __init__(self, seed=2):

        self.seed = seed
        if seed:
            random.seed(seed)
    def check_if_node_leaf(self, edges, nodeID):
        for edge_dict in edges:
            if edge_dict['fromID'] == nodeID:
                return False
        return True

    def get_node_parent(self, aif, nodeID):

        rel_nodes_ids = []
        for edge_dict in aif['edges']:
            if edge_dict['toID'] == nodeID:
                rel_nodes_ids.append(edge_dict['fromID'])

        parents = []
        for edge_dict in aif['edges']:
            if edge_dict['toID'] in rel_nodes_ids:

                node_types = [
                    node_dict['type'] for node_dict in aif['nodes'] if node_dict['nodeID'] == edge_dict['fromID']
                ]
                if node_types:
                    if node_types[0] == "I":
                        parents.append(edge_dict['fromID'])
        if parents:
            return parents[0]
        else:
            return None

    def get_leafs_parents(self, aif):
        leafs_parents = {}

        for node_dict in aif['nodes']:
            if node_dict['type'] == 'I':
                if self.check_if_node_leaf(aif['edges'], node_dict['nodeID']):

                    parent = self.get_node_parent(aif, node_dict['nodeID'])

                    if parent:
                        if parent not in leafs_parents:
                            leafs_parents[parent] = []
                        leafs_parents[parent].append(node_dict['nodeID'])
        return leafs_parents

    def create_unique_mapping(self, elements):

        if len(elements) < 2:
            raise ValueError("List must contain at least two elements for a valid mapping.")

        # try N times to generate a unique mapping. If not - whatever
        for i in range(100):
            shuffled = list(sorted(elements, key=lambda x: random.uniform(0,1)))
            if all(a != b for a, b in zip(elements, shuffled)):
                break

        return dict(zip(elements, shuffled))


    def nodeDict_by_nodeID(self, aif, nodeID):
        for node_dict in aif['nodes']:
            if node_dict['nodeID'] == nodeID:
                return node_dict
    def swap_leafs(self, aif, leaf_i_nodes_to_parent):

        swapped_leafs_aif = {
            "nodes": [],
            "edges": deepcopy(aif['edges'])
        }

        reordered_leafs_map = {}
        for leafs in leaf_i_nodes_to_parent.values():
            reordered_leafs_map.update(self.create_unique_mapping(leafs))



        for node_dict in aif['nodes']:
            swapped_node_dict = deepcopy(node_dict)
            if node_dict['nodeID'] in reordered_leafs_map:
                swapped_node_dict['text_occ_idx'] = self.nodeDict_by_nodeID(
                    aif, reordered_leafs_map[node_dict['nodeID']]
                )['text_occ_idx']
            swapped_leafs_aif['nodes'].append(swapped_node_dict)

        return swapped_leafs_aif

    def generate_pair(self, aif):

        leaf_i_nodes_to_parent = self.get_leafs_parents(aif)
        leaf_i_nodes_to_parent = {k:v for k,v in leaf_i_nodes_to_parent.items() if len(v) >= 2}

        if not len(leaf_i_nodes_to_parent):
            return {}, False

        swapped_leafs_aif = self.swap_leafs(aif, leaf_i_nodes_to_parent)

        return {
            "aif_1": aif.copy(),
            "aif_2": swapped_leafs_aif,
            "are_strategies_similar": True
        }, True




