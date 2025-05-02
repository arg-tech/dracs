from aif_transforms_gens.leaf_swap import LeafsSwapsAIF
from aif_transforms_gens.bottom_up import BottomUpPairAIFGeneration
from aif_transforms_gens.shuffle_aif_occurances import ShuffleIOccurancesAIF
from aif_transforms_gens.generator_tree_aif import TreeAIFGenerator

import os, json, random
from tqdm import tqdm



def generate_save_tree_aifs_as_nodeset(
        savedir,
        N=50,

        min_depth=8,
        max_depth=32,

        p_width=0.5,
        max_n_width=8,

        min_n_subtrees=3,
        max_n_subtrees=8,

        min_leafs=1,
        max_leafs=3,

        seed=2
):
    os.makedirs(savedir, exist_ok=True)
    generator = TreeAIFGenerator(seed=seed)

    for i in tqdm(range(N)):
        depth = random.randint(a=min_depth, b=max_depth)
        gen_pair_dict = generator.generate_pair(depth=depth, p_width=p_width,
                                                max_n_subtrees=max_n_subtrees,
                                                max_n_width=max_n_width,
                                                min_n_subtrees=min_n_subtrees,
                                                min_leafs=min_leafs, max_leafs=max_leafs
                                                )

        with open(os.path.join(savedir, f"SynthTreeNodesetDFS-{i}.json"), 'w') as f:
            json.dump(gen_pair_dict['dfs_indexed_tree_aif'], f)
        with open(os.path.join(savedir, f"SynthTreeNodesetBFS-{i}.json"), 'w') as f:
            json.dump(gen_pair_dict['bfs_indexed_tree_aif'], f)

def gen_leafs_swap(savedir, aif_load_dir, seed=2):

    SAVE_SUBDIR = "Similar--LeafsSwap"
    SAVE_SUBDIR = os.path.join(savedir, SAVE_SUBDIR)
    os.makedirs(SAVE_SUBDIR, exist_ok=True)

    generator = LeafsSwapsAIF(seed=seed)

    for filename in tqdm(os.listdir(aif_load_dir)):
        if filename.endswith('.json'):
            aif = json.load(
                open(os.path.join(aif_load_dir, filename), 'r')
            )
            gen_pair_dict, is_success = generator.generate_pair(
                aif=aif
            )

            if is_success:
                nodeset_name = filename.replace(".json", "--indexed_pair.json")
                with open(os.path.join(SAVE_SUBDIR, nodeset_name), 'w') as f:
                    json.dump(gen_pair_dict, f)

def bottom_up_reverse_from_aif(savedir, aif_load_dir, seed=2):

    SAVE_SUBDIR = "NotSimilar--BottomUp"
    SAVE_SUBDIR = os.path.join(savedir, SAVE_SUBDIR)
    os.makedirs(SAVE_SUBDIR, exist_ok=True)

    generator = BottomUpPairAIFGeneration(seed=seed)

    for filename in tqdm(os.listdir(aif_load_dir)):
        if filename.endswith('.json'):
            aif = json.load(
                open(os.path.join(aif_load_dir, filename), 'r')
            )
            gen_pair_dict, is_success = generator.generate_pair_from_existent_aif(
                aif=aif
            )

            if is_success:
                nodeset_name = filename.replace(".json", "--indexed_pair.json")
                with open(os.path.join(SAVE_SUBDIR, nodeset_name), 'w') as f:
                    json.dump(gen_pair_dict, f)

def gen_idx_shuffle(savedir, aif_load_dir, seed=2, min_perc_changed=0.7, min_num_i_nodes=8):

    SAVE_SUBDIR = "NotSimilar--ShuffleIDX"
    SAVE_SUBDIR = os.path.join(savedir, SAVE_SUBDIR)
    os.makedirs(SAVE_SUBDIR, exist_ok=True)

    shuffler = ShuffleIOccurancesAIF(seed=seed)

    for filename in tqdm(os.listdir(aif_load_dir)):
        if filename.endswith('.json'):
            aif = json.load(
                open(os.path.join(aif_load_dir, filename), 'r')
            )
            gen_pair_dict, is_success = shuffler.generate_pair(aif=aif,
                                                               min_perc_changed=min_perc_changed,
                                                               min_num_i_nodes=min_num_i_nodes)

            if is_success:
                nodeset_name = filename.replace(".json", "--indexed_pair.json")
                with open(os.path.join(SAVE_SUBDIR, nodeset_name), 'w') as f:
                    json.dump(gen_pair_dict, f)

def apply_methods(loaddir, saveddir):
    os.makedirs(saveddir, exist_ok=True)
    gen_leafs_swap(
        savedir=saveddir,
        aif_load_dir=loaddir,
        seed=2
    )
    bottom_up_reverse_from_aif(
        savedir=saveddir,
        aif_load_dir=loaddir,
        seed=2
    )

    gen_idx_shuffle(
        savedir=saveddir,
        aif_load_dir=loaddir,
        seed=2
    )


if __name__ == '__main__':
    generate_save_tree_aifs_as_nodeset(
        savedir="data/STrees",
        N=75,
        min_depth=4,
        max_depth=10,
        p_width=0.65,
        max_n_width=5,
        min_n_subtrees=3,
        max_n_subtrees=6,
        seed=2,
        min_leafs=2,
        max_leafs=5
    )

    US2016Dtv_LOADDIR = "data/US2016D1tv"
    US2016Dtv_SAVEDIR = "US2016D1tv_pairs"
    apply_methods(loaddir=US2016Dtv_LOADDIR, saveddir=US2016Dtv_SAVEDIR)

    US2016Dtv_LOADDIR = "data/US2016R1tv"
    US2016Dtv_SAVEDIR = "US2016R1tv_pairs"
    apply_methods(loaddir=US2016Dtv_LOADDIR, saveddir=US2016Dtv_SAVEDIR)

    US2016Dtv_LOADDIR = "data/US2016G1tv"
    US2016Dtv_SAVEDIR = "US2016G1tv_pairs"
    apply_methods(loaddir=US2016Dtv_LOADDIR, saveddir=US2016Dtv_SAVEDIR)

    US2016Dtv_LOADDIR = "data/UNSC/"
    US2016Dtv_SAVEDIR = "UNSC_pairs"
    apply_methods(loaddir=US2016Dtv_LOADDIR, saveddir=US2016Dtv_SAVEDIR)
