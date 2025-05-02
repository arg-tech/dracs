import random
import networkx as nx
from feature_extraction import AIFTimeFillingFeatureExtractor
from copy import deepcopy

class BottomUpPairAIFGeneration:

    def __init__(self, seed=2):
        self.seed = seed
        if seed:
            random.seed(seed)


        self.ya_to_nodes = {
            "I": [
                ("YA", "Asserting"),
                ("YA", "Disagreeing"),
                ("YA", "Rhetorical Questioning"),
                ("YA", "Pure Questioning"),
                ("YA", "Agreeing")
            ],
            "RA": [
                ("YA", "Arguing")
            ],
            "MA": [
                ("YA", "Restating"),
                ("YA", "Default Illocuting"),

            ],
            "CA": [("YA", "Disagreeing")]
        }

        self.rel_nodes_texts = [
            ("RA", "Default Inference"),
            ("MA", "Default Rephrase"),
            ("CA", "Default Conflict")
        ]

        # will be created in self.generate_pair
        self.feature_extractor = AIFTimeFillingFeatureExtractor()

    def generate_depth_aif(self, depth, aif, start_node=0):

        # generate I nodes
        for i in range(depth):
            aif['nodes'].append(
                {
                    "type": "I",
                    "text": f"I: {i+start_node}",
                    "nodeID": str(i+start_node)
                }
            )

        for i in range(depth - 1):
            random_rel_node_type, random_rel_node_text = random.choice(self.rel_nodes_texts)
            aif['nodes'].append(
                {
                    "type": random_rel_node_type,
                    "text": random_rel_node_text,
                    "nodeID": str(depth + i + start_node)
                }
            )
            next_edge_id = self.get_next_available_edgeID(aif=aif)
            aif['edges'].append(
                {
                    "edgeID": str(next_edge_id),
                    "fromID": str(i + start_node),
                    "toID": str(depth + i + start_node)
                }
            )
            aif['edges'].append({
                "edgeID": str(next_edge_id + 1),
                "fromID": str(depth + i + start_node),
                "toID": str(i + 1 + start_node)
            })

        return aif, 0 + start_node

    def get_next_available_nodeID(self, aif):
        all_nodes = [int(node_dict["nodeID"]) for node_dict in aif['nodes']]
        if all_nodes:
            return max(all_nodes) + 1
        return 0

    def get_next_available_edgeID(self, aif):
        all_edges = [int(node_dict["edgeID"]) for node_dict in aif['edges']]
        if all_edges:
            return max(all_edges) + 1
        return 0

    def gen_width_sections(self, max_n_width, i_nodeID, aif):

        startNodeID = self.get_next_available_nodeID(aif=aif)
        aif, root_node_id = self.generate_depth_aif(
            depth=max_n_width,
            aif=aif,
            start_node=startNodeID
        )

        # create connection branch
        connectEdgeID = self.get_next_available_edgeID(aif=aif)
        connectNodeID = self.get_next_available_nodeID(aif=aif)

        random_rel_type, random_rel_text = random.choice(self.rel_nodes_texts)
        aif['nodes'].append(
            {
                "nodeID": str(connectNodeID),
                "text": random_rel_text,
                'type': random_rel_type
            }
        )
        aif['edges'].append(
            {
                "edgeID": str(connectEdgeID),
                "fromID": str(i_nodeID),
                'toID': str(connectNodeID)
            }
        )
        aif['edges'].append(
            {
                "edgeID": str(connectEdgeID + 1),
                "fromID": str(connectNodeID),
                'toID': str(root_node_id)
            }
        )

        return aif

    def gen_indexed_aif(self, list_nodesNums_path):
        indexed_aif = {
            "nodes": [],
            "edges": deepcopy(self.feature_extractor.aif['edges'])
        }

        completed_nodes = []
        for node_i in range(len(self.feature_extractor.aif['nodes'])):

            nodeID = self.feature_extractor.aif['nodes'][node_i]['nodeID']
            nodeNum = self.feature_extractor.nodeID_to_num[nodeID]
            to_append_node_dict = {k: v for k, v in self.feature_extractor.aif['nodes'][node_i].items()}

            if self.feature_extractor.aif['nodes'][node_i]['type'] == "I":
                if nodeNum not in completed_nodes and nodeNum in list_nodesNums_path:
                    to_append_node_dict['text_occ_idx'] = list_nodesNums_path.index(nodeNum)
                    completed_nodes.append(nodeNum)

            indexed_aif['nodes'].append(to_append_node_dict)
        return indexed_aif


    def get_dfs_indexed_aif(self, source_num):

        dfs_path = list(nx.dfs_preorder_nodes(G=self.feature_extractor.nx_graph, source=source_num))
        # dfs_path = list(nx.dfs_edges(G=self.feature_extractor.nx_graph, source=source_num))
        indexed_aif = self.gen_indexed_aif(dfs_path)

        return indexed_aif

    def get_bfs_indexed_aif(self, source_num):
        edges = list(nx.bfs_edges(G=self.feature_extractor.nx_graph, source=source_num))
        # self.bfs_edges = edges

        edges = [list(x) for x in edges]
        edges = sum(edges, [])
        self.bfs_flatten = edges

        indexed_aif = self.gen_indexed_aif(edges)
        return indexed_aif

    def add_ya_nodes(self, aif):
        append_ya_nodes = []
        append_ya_edges = []

        start_nodeID = self.get_next_available_nodeID(aif)
        start_edgeID = self.get_next_available_edgeID(aif)


        for i, node_dict in enumerate(aif['nodes']):
            _, random_ya_text = random.choice(
                self.ya_to_nodes[node_dict['type']]
            )
            append_ya_nodes.append(
                {
                    "nodeID": str(start_nodeID + i),
                    "text": random_ya_text,
                    "type": "YA"
                }
            )
            append_ya_edges.append(
                {
                    "edgeID": str(start_edgeID + 1),
                    "fromID": str(start_nodeID + i),
                    "toID": node_dict['nodeID']
                }
            )


        aif['nodes'] += append_ya_nodes
        aif['edges'] += append_ya_edges


    def reverse_index(self, dfs_indexed_aif):

        all_text_occ = [x['text_occ_idx'] for x in dfs_indexed_aif['nodes'] if 'text_occ_idx' in x]
        all_text_occ = list(sorted(all_text_occ))[::-1]

        reversed_aif = {
            "nodes": [],
            "edges": deepcopy(dfs_indexed_aif['edges'])
        }

        for node_dict in dfs_indexed_aif['nodes']:
            copy_node_dict = deepcopy(node_dict)
            if 'text_occ_idx' in node_dict:
                copy_node_dict['text_occ_idx'] = all_text_occ.index(node_dict['text_occ_idx'])
            reversed_aif['nodes'].append(copy_node_dict)
        return reversed_aif


    def ya_node(self, aif, nodeID):
        for node_dict in aif['nodes']:
            if node_dict['nodeID'] == nodeID:
                return node_dict['type'] == "YA"
        return False

    def no_in_rel_connections(self, aif, nodeID):
        for edge_dict in aif['edges']:
            if edge_dict['toID'] == nodeID:
                if not self.ya_node(aif,edge_dict['fromID']):
                    return False
        return True

    def get_source_num_from_existing(self, aif):

        potential_sources = []
        i_nodes = []
        for node_dict in aif['nodes']:
            if node_dict['type'] == "I" and 'text_occ_idx' in node_dict:
                i_nodes.append(node_dict)
                if self.no_in_rel_connections(aif, node_dict['nodeID']):
                    potential_sources.append(node_dict)
        if len(potential_sources) == 1:
            return self.feature_extractor.nodeID_to_num[potential_sources[0]['nodeID']]
        elif len(potential_sources) == 0:
            nodeID = sorted(i_nodes, key=lambda x: x['text_occ_idx'])[0]['nodeID']
            return self.feature_extractor.nodeID_to_num[nodeID]
        else:
            nodeID = sorted(potential_sources, key=lambda x: x['text_occ_idx'])[0]['nodeID']
            return self.feature_extractor.nodeID_to_num[nodeID]


    def is_i_source(self, nodeID, aif, cycles_nodeIDs, comp):
        unique_nodeIDs_cycles = sum(cycles_nodeIDs, [])

        node_dict = [node_dict for node_dict in aif['nodes'] if node_dict['nodeID'] == nodeID][0]
        if node_dict['type'] != "I":
            return False



        edges_from = [
            edge_dict for edge_dict in aif['edges'] if edge_dict['fromID'] == nodeID
        ]

        edges_to = [
            edge_dict for edge_dict in aif['edges'] if edge_dict['toID'] == nodeID
        ]

        if len(edges_from):
            return False

        if node_dict['nodeID'] in unique_nodeIDs_cycles:
            comp_occ = [
                node_dict for node_dict in aif['nodes'] if node_dict['nodeID'] in comp
            ]
            initial_comp_occ = sorted(comp_occ, key=lambda x: x['text_occ_idx'])[0]

            if initial_comp_occ['nodeID'] == nodeID:
                return False
        else:
            return bool(len(edges_to) == 0)



    def generate_pair_from_existent_aif(self, aif):

        self.feature_extractor.build_graph(
            nodes_dicts=aif['nodes'],
            edges_dicts=aif['edges']
        )

        reversed_dfs_indexed_aif = self.reverse_index(dfs_indexed_aif=aif)

        return {
            "aif_1": reversed_dfs_indexed_aif,
            "aif_2": deepcopy(aif),
            "are_strategies_similar": False
        }, True

        # except Exception as e:
        #     print(str(e))
        #     return {}, False


    def generate_pair(self, depth, p_width, max_n_width):

        base_aif = {
            "nodes": [],
            "edges": []
        }

        # long aif, one by one in depth
        base_aif, last_i_node = self.generate_depth_aif(depth=depth, aif=base_aif)

        # randomly go for each I node and width subgraphs
        aif_node_ids = [
            node_dict['nodeID'] for node_dict in base_aif['nodes'] if node_dict['type'] == "I"
        ]
        for i_nodeID in aif_node_ids:
            if p_width >= random.uniform(0,1):
                base_aif = self.gen_width_sections(
                    max_n_width=max_n_width,
                    i_nodeID=i_nodeID,
                    aif=base_aif
                )

        # dfs and bfs reidexing
        self.feature_extractor.build_graph(
            nodes_dicts=base_aif['nodes'],
            edges_dicts=base_aif['edges']
        )
        source_num = self.feature_extractor.nodeID_to_num[str(last_i_node)]

        dfs_indexed_aif = self.get_dfs_indexed_aif(source_num=source_num)
        reversed_dfs_indexed_aif = self.reverse_index(dfs_indexed_aif=dfs_indexed_aif)

        return {
            "aif_1": reversed_dfs_indexed_aif,
            "aif_2": dfs_indexed_aif,
            "are_strategies_similar": False
        }





