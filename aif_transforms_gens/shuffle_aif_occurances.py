import random
from copy import deepcopy

class ShuffleIOccurancesAIF:
    def __init__(self, seed=2):

        self.seed = seed
        if seed:
            random.seed(seed)

    def generate_random_idx_map(self, aif, min_perc_changed=0.7):
        text_occ = [
            node_dict['text_occ_idx'] for node_dict in aif['nodes'] if 'text_occ_idx' in node_dict
        ]

        highest_perc_shuffle, best_shuffle = -1.0, {}

        for _ in range(1000):

            randomized_text_occ = list(sorted(
                text_occ, key=lambda x: random.uniform(0,1)
            ))

            shuffle_perc = sum([randomized_text_occ[i] != text_occ[i] for i in range(len(randomized_text_occ))])/len(randomized_text_occ)

            if highest_perc_shuffle < shuffle_perc:
                highest_perc_shuffle = shuffle_perc
                best_shuffle = deepcopy(randomized_text_occ)

            if shuffle_perc >= min_perc_changed:
                break


        return {
            occ: random_occ for occ, random_occ in zip(text_occ, best_shuffle)
        }

    def shuffle_aif_idx(self, random_idx_map, aif):
        shuffled_aif = {
            "nodes": deepcopy(aif['nodes']),
            "edges": deepcopy(aif['edges'])
        }

        for node_dict_i in range(len(shuffled_aif['nodes'])):
            if 'text_occ_idx' in shuffled_aif['nodes'][node_dict_i]:
                shuffled_aif['nodes'][node_dict_i]['text_occ_idx'] = random_idx_map[shuffled_aif['nodes'][node_dict_i]['text_occ_idx']]

        return shuffled_aif

    def generate_pair(self, aif, min_perc_changed=0.7, min_num_i_nodes=8):

        n_i_nodes = len([x for x in aif['nodes'] if x['type'] == "I"])
        if n_i_nodes < min_num_i_nodes:
            return {}, False


        random_idx_map = self.generate_random_idx_map(aif, min_perc_changed)
        shuffled_aif = self.shuffle_aif_idx(random_idx_map=random_idx_map, aif=aif)
        return {
            "aif_1": aif.copy(),
            "aif_2": shuffled_aif,
            "are_strategies_similar": False
        }, True




