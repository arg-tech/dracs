from dtaidistance import dtw
from tslearn.metrics import dtw_path


class Metrics:

    @staticmethod
    def dtw_distance(
            aif_1_ts_features,
            aif_2_ts_features
    ):
        dist = dtw.distance(
            aif_1_ts_features,
            aif_2_ts_features
        )
        return dist

    @staticmethod
    def multidimensional_dtw_similarity(
            aif_1_ts_features,
            aif_2_ts_features
    ):
        path, smt_score = dtw_path(aif_1_ts_features, aif_2_ts_features)
        return smt_score
        # return sum(dtw.distance(aif_1_ts_features[:, d], aif_2_ts_features[:, d]) for d in range(aif_1_ts_features.shape[1]))
