from itertools import combinations
import json, os
from tqdm import tqdm
import numpy as np
from metrics import Metrics
from feature_extraction import AIFTimeChunkSplitter

if __name__ == '__main__':
    # method = "pairs_st_weighted"
    method = "binary"

    save_nodeset_name = True

    # savename = "US2016D1tv"
    # loaddir = "data/US2016D1tv_Ordered"
    # loadmeta = 'data/US2016D1tv_filtered_accepted_pathes_meta.json'

    savename = "US2016R1tv"
    loaddir = "data/US2016R1tv_Ordered"
    loadmeta = 'data/US2016R1tv_filtered_accepted_pathes_meta.json'

    savedir = f"result{savename}-SNS/{method}_dtwSimScore_test_runs/"
    os.makedirs(savedir, exist_ok=True)

    speech_meta = json.load(open(loadmeta, 'r'))

    countries_vectors_save_dir = f'result{savename}-SNS/{method}_dtwSimScore_vectors/'
    os.makedirs(countries_vectors_save_dir, exist_ok=True)

    unique_days = set([x['day'] for x in speech_meta if x['day']])



    def save_vectors(vectors, day, selected_sample, countries_vectors_save_dir, save_nodeset_name=True):
        country = selected_sample['speaker']
        if save_nodeset_name:
            nodeset = os.path.basename(selected_sample["filepath"]).replace(".json", "")
            country += " " + nodeset

        if f"{day}--{country}-vectors.npy" not in os.listdir(countries_vectors_save_dir):
            np.save(os.path.join(countries_vectors_save_dir, f"{day}--{country}-vectors"), vectors)


    for day in unique_days:
        selected_samples = [
            x for x in speech_meta if x['day'] == day
        ]

        # Create an ordered list of turns
        dist_matrix = np.zeros((len(selected_samples), len(selected_samples)))

        countries = [
            x['speaker'] for x in selected_samples
        ]

        if len(set(countries)) > 1:

            for i, j in tqdm(combinations(list(range(len(selected_samples))), 2)):

                aif_filepath_1 = os.path.join(loaddir, os.path.basename(selected_samples[i]['filepath']))
                aif_filepath_2 = os.path.join(loaddir, os.path.basename(selected_samples[j]['filepath']))


                aif_1 = json.load(
                    open(
                        aif_filepath_1,
                        'r'
                    )
                )
                aif_2 = json.load(
                    open(
                        aif_filepath_2,
                        'r'
                    )
                )


                try:
                    aif_1_ts_features, feature_names = AIFTimeChunkSplitter.get_time_features(
                        aif=aif_1, aif_method=method, verbose=False
                    )
                    aif_2_ts_features, feature_names = AIFTimeChunkSplitter.get_time_features(
                        aif=aif_2, aif_method=method, verbose=False
                    )

                    if aif_1_ts_features.shape and aif_2_ts_features.shape:

                        # if 'feature_names.json' not in os.listdir(savedir):
                        with open(os.path.join(savedir, 'feature_names.json'), 'w') as f:
                            json.dump(feature_names, f)

                        save_vectors(
                            vectors=aif_1_ts_features,
                            day=day,
                            selected_sample=selected_samples[i],
                            countries_vectors_save_dir=countries_vectors_save_dir,
                            save_nodeset_name=save_nodeset_name
                        )
                        save_vectors(
                            vectors=aif_2_ts_features,
                            day=day,
                            selected_sample=selected_samples[j],
                            countries_vectors_save_dir=countries_vectors_save_dir,
                            save_nodeset_name=save_nodeset_name
                        )

                        dist = Metrics.multidimensional_dtw_similarity(
                            aif_1_ts_features=aif_1_ts_features,
                            aif_2_ts_features=aif_2_ts_features
                        )

                        dist_matrix[i, j] = dist
                        dist_matrix[j, i] = dist
                except Exception as e:
                    print(str(e))

            dist_matrix = dist_matrix.tolist()
            with open(os.path.join(savedir, f'{day}-dist_matrix.json'), 'w') as f:
                json.dump(dist_matrix, f)


        with open(os.path.join(savedir, f'{day}-countries.json'), 'w') as f:
            json.dump(countries, f)
