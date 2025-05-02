# DRACS: Diachronic Representation of Argument Construction Styles

---

This repo contains a code for `DRACS: Diachronic Representation of Argument Construction Styles` paper.


# How to run and customize the code

## Setup
Install requirements from [requirements.txt](requirements.txt):

```commandline
pip install -r requirements.txt
```

## Inference
Refer to tutorial notebook in [Extract_DRACS_features.ipynb](tutorials/Extract_DRACS_features.ipynb).

---

# Contents

* [aif_transforms_gens](aif_transforms_gens) and [generate_synth_data.py](generate_synth_data.py): code for transformations and Tree AIF generation.
* [data](data): datasets used in paper.
* [tutorials](tutorials): tutorial notebooks.
* [calc_distances__graph_combs.py](calc_distances__graph_combs.py) and [calc_distances__process_strategies_combs.py](calc_distances__process_strategies_combs.py): scripts for calculating representations between different transformer pairs.
* [feature_extraction.py](feature_extraction.py): DRACS feature extractor.
* [metrics.py](metrics.py): DTW metrics.


# Cite

If you used our proposed approach, please cite as follows:

```text
NA
```