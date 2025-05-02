from itertools import combinations
import json, os
from tqdm import tqdm
from aif_graph_utils import GraphAIF, aif_calculate_spectral_distance
import numpy as np


# method = "pairs_st_weighted"
method = "binary"

savename = "US2016D1tv"
loaddir = "data/US2016D1tv_Ordered"
loadmeta = 'data/US2016D1tv_filtered_accepted_pathes_meta.json'


savedir = f"result{savename}/{method}_matrices_per_day/"
os.makedirs(savedir, exist_ok=True)

speech_meta = json.load(open(loadmeta, 'r'))


unique_days = set([x['day'] for x in speech_meta if x['day']])

for day in unique_days:
    selected_samples = [
        x for x in speech_meta if x['day'] == day
    ]


    dist_matrix = np.zeros((len(selected_samples), len(selected_samples)))

    countries = [
        x['speaker'] for x in selected_samples
    ]

    if len(set(countries)) > 1:

        for i,j in tqdm(combinations(list(range(len(selected_samples))),2)):

            aif_filepath_1 = os.path.join(loaddir, os.path.basename(selected_samples[i]['filepath']))
            aif_filepath_2 = os.path.join(loaddir, os.path.basename(selected_samples[j]['filepath']))
            aif_1 = json.load(open(aif_filepath_1, 'r'))
            aif_2 = json.load(open(aif_filepath_2, 'r'))

            aif_1 = GraphAIF(aif_1, method=method)
            aif_2 = GraphAIF(aif_2, method=method)

            dist = aif_calculate_spectral_distance(aif_1, aif_2)
            dist_matrix[i,j] = dist
            dist_matrix[j,i] = dist

        dist_matrix = dist_matrix.tolist()
        with open(os.path.join(savedir, f'{day}-dist_matrix.json'), 'w') as f:
            json.dump(dist_matrix, f)

        with open(os.path.join(savedir, f'{day}-countries.json'), 'w') as f:
            json.dump(countries, f)

