import random
import networkx as nx
from feature_extraction import AIFTimeFillingFeatureExtractor
from copy import deepcopy


class TreeAIFGenerator:
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

        self.Crel_nodes_texts = [
            ("RA", "Default Inference"),
            ("MA", "Default Rephrase"),
            ("CA", "Default Conflict")
        ]

        self.feature_extractor = AIFTimeFillingFeatureExtractor()

    def get_next_available_nodeID(self, aif):
        all_nodes = [int(node_dict["nodeID"]) for node_dict in aif['nodes']]
        if all_nodes:
            return max(all_nodes) + 1
        return 0
    def gen_width_sections(self, max_n_width, i_nodeID, aif, min_leafs, max_leafs):

        startNodeID = self.get_next_available_nodeID(aif=aif)
        aif, root_node_id, final_node_id = self.generate_depth_aif(
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

        n_leafs_attach = random.randint(min_leafs, max_leafs)
        for leaf_i in range(n_leafs_attach):
            addEdgeID = self.get_next_available_edgeID(aif=aif)
            addNodeID = self.get_next_available_nodeID(aif=aif)

            random_rel_type, random_rel_text = random.choice(self.rel_nodes_texts)
            aif['nodes'] += [
                {
                    "nodeID": str(addNodeID),
                    "type": "I",
                    "text": f"I: {addNodeID} -> Leaf;"
                },
                {
                    "nodeID": str(addNodeID + 1),
                    "type": random_rel_type,
                    "text": random_rel_text
                }
            ]
            aif['edges'] += [
                {
                    "edgeID": str(addEdgeID),
                    "fromID": str(final_node_id),
                    "toID": str(addNodeID + 1)
                },
                {
                    "edgeID": str(addEdgeID + 1),
                    "fromID": str(addNodeID + 1),
                    "toID": str(addNodeID)
                }
            ]

            if "None" in [x['nodeID'] for x in aif['nodes']] or "None" in [x['fromID'] for x in aif['edges']]:
                print()

        return aif

    def get_next_available_edgeID(self, aif):
        all_edges = [int(node_dict["edgeID"]) for node_dict in aif['edges']]
        if all_edges:
            return max(all_edges) + 1
        return 0

    def generate_depth_aif(self, depth, aif, start_node=0):

        # generate I nodes
        for i in range(depth):
            aif['nodes'].append(
                {
                    "type": "I",
                    "text": f"I: {i + start_node}",
                    "nodeID": str(i + start_node)
                }
            )

        final_node_id = None
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
            final_node_id = i + 1 + start_node

        return aif, 0 + start_node, final_node_id


    def populate_with_ya_nodes(self, aif):

        existing_node_dicts = deepcopy(aif['nodes'])
        for node_dict in existing_node_dicts:
            random_ya_type, random_ya_text = random.choice(self.ya_to_nodes[node_dict['type']])

            next_nodeID = self.get_next_available_nodeID(aif)
            aif['nodes'].append(
                {
                    "type": random_ya_type,
                    "nodeID": str(next_nodeID),
                    "text": random_ya_text
                }
            )

            next_edgeID = self.get_next_available_edgeID(aif)
            aif['edges'].append(
                {
                    "edgeID": str(next_edgeID),
                    "fromID": str(next_nodeID),
                    "toID": node_dict['nodeID']
                }
            )
        return aif

    def gen_indexed_aif(self, list_nodesNums_path):
        indexed_aif = {
            "nodes": [],
            "edges": deepcopy(self.feature_extractor.aif['edges'])
        }

        issue_nodes_idx = []
        completed_nodes = []


        for node_i in range(len(self.feature_extractor.aif['nodes'])):

            nodeID = self.feature_extractor.aif['nodes'][node_i]['nodeID']
            nodeNum = self.feature_extractor.nodeID_to_num[nodeID]
            to_append_node_dict = {k: v for k, v in self.feature_extractor.aif['nodes'][node_i].items()}

            if self.feature_extractor.aif['nodes'][node_i]['type'] == "I":
                if nodeNum not in completed_nodes:
                    if nodeNum in list_nodesNums_path:
                        to_append_node_dict['text_occ_idx'] = list_nodesNums_path.index(nodeNum)
                        completed_nodes.append(nodeNum)
                    else:
                        issue_nodes_idx.append(node_i)

            indexed_aif['nodes'].append(to_append_node_dict)


        for i, issue_node_idx in enumerate(issue_nodes_idx):
            to_append_node_dict = {k: v for k, v in self.feature_extractor.aif['nodes'][issue_node_idx].items()}
            to_append_node_dict['text_occ_idx'] = max(list_nodesNums_path) + i + len(self.feature_extractor.aif['nodes'])
            indexed_aif['nodes'].append(to_append_node_dict)

        return indexed_aif

    def get_dfs_indexed_aif(self, source_num, aif):
        dfs_path = list(nx.dfs_preorder_nodes(G=self.feature_extractor.nx_graph, source=source_num))

        i_nodes = [self.feature_extractor.nodeID_to_num[node_dict['nodeID']] for node_dict in aif['nodes'] if node_dict['type'] == "I"]
        for nodenum in dfs_path:
            if nodenum not in i_nodes:
                nodenum_2_id = {v:k for k,v in self.feature_extractor.nodeID_to_num.items()}
                nodeid = nodenum_2_id[nodenum]
            assert nodenum in dfs_path

        indexed_aif = self.gen_indexed_aif(dfs_path)
        return indexed_aif

    def get_bfs_indexed_aif(self, source_num, aif):
        edges = list(nx.bfs_edges(G=self.feature_extractor.nx_graph, source=source_num))
        edges = [list(x) for x in edges]
        edges = sum(edges, [])

        i_nodes = [self.feature_extractor.nodeID_to_num[node_dict['nodeID']] for node_dict in aif['nodes'] if node_dict['type'] == "I"]
        for nodenum in i_nodes:
            if nodenum not in edges:
                nodenum_2_id = {v: k for k, v in self.feature_extractor.nodeID_to_num.items()}
                nodeid = nodenum_2_id[nodenum]
                print()
            assert nodenum in edges

        indexed_aif = self.gen_indexed_aif(edges)
        return indexed_aif


    def generate_pair(self, depth, p_width, max_n_width, min_n_subtrees, max_n_subtrees, min_leafs, max_leafs, how_index="dfs"):

        base_aif = {
            "nodes": [],
            "edges": []
        }

        # long aif, one by one in depth
        base_aif, last_i_node, final_node_id = self.generate_depth_aif(depth=depth, aif=base_aif)


        # randomly go for each I node and width subgraphs
        aif_node_ids = [
            node_dict['nodeID'] for node_dict in base_aif['nodes'] if node_dict['type'] == "I"
        ]

        for i_nodeID in aif_node_ids:
            if p_width >= random.uniform(0,1):
                n_subtrees = random.randint(min_n_subtrees, max_n_subtrees)
                for _ in range(n_subtrees):
                    n_width = random.randint(2, max_n_width+1)
                    base_aif = self.gen_width_sections(
                        max_n_width=n_width,
                        i_nodeID=i_nodeID,
                        aif=base_aif,
                        min_leafs=min_leafs,
                        max_leafs=max_leafs
                    )

        base_aif = self.populate_with_ya_nodes(base_aif)

        self.feature_extractor.build_graph(
            nodes_dicts=base_aif['nodes'],
            edges_dicts=base_aif['edges']
        )
        source_num = self.feature_extractor.nodeID_to_num[str(last_i_node)]

        dfs_indexed_aif = self.get_dfs_indexed_aif(source_num=source_num, aif=base_aif)
        bfs_indexed_aif = self.get_bfs_indexed_aif(source_num=source_num, aif=base_aif)

        # eval correctness
        for node_dict in dfs_indexed_aif['nodes']:
            if node_dict['type'] == 'I':
                assert 'text_occ_idx' in node_dict

        for node_dict in bfs_indexed_aif['nodes']:
            if node_dict['type'] == 'I':
                assert 'text_occ_idx' in node_dict


        return {
            "bfs_indexed_tree_aif": bfs_indexed_aif,
            "dfs_indexed_tree_aif": dfs_indexed_aif,
        }
