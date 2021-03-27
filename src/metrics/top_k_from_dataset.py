from src.data.flat_dataset_factory import FlatDatasetFactory
from src.instruction_utility import *
import numpy as np

import tensorflow_addons as tfa

class TopKAccuracy:
    def __init__(self, model, dataset, distance_metric="L2"):
        self.model = model
        self.dataset = dataset

        self.distance_metric = distance_metric

        self.prediction = self.get_prediction()

        self.labels = np.concatenate([y for x, y in self.dataset], axis=0)

        self.top_k = {}

    def get_prediction(self):
        prediction = self.model.predict(self.dataset)
        if self.distance_metric == "angular":
            prediction = prediction/np.linalg.norm(prediction, axis=1, keepdims=True)
            print(prediction.shape)
        return prediction

    def get_top_k_accuracies(self, k_list=[1, 5, 10]):
        self.top_k = {}
        self.top_k = self.initalize_top_k_dict(k_list)

        for i in range(self.prediction.shape[0]):
            sorted_match_bool = self.get_sorted_match_bool_for_index(i)
            for k in k_list:
                self.top_k["top_" + str(k)] += int(np.any(sorted_match_bool[1:k + 1]))

        return self.normalize_top_k_dict()

    def initalize_top_k_dict(self, k_list):
        self.top_k = {}
        for k in k_list:
            self.top_k["top_" + str(k)] = 0.
        return self.top_k

    def get_sorted_match_bool_for_index(self, index):
        if self.distance_metric == "L2":
            distances = np.linalg.norm(self.prediction - self.prediction[index], axis=1)
        elif self.distance_metric == "angular":
            cosine_similarity = np.matmul(self.prediction, np.reshape(self.prediction[index], (-1, 1)))
            distances = 1. - cosine_similarity
            distances = np.maximum(distances, 0.0)
            distances = distances.flatten()
        else:
            print(f"Unknown distance metric: {self.distance_metric}")
        sorted_index = np.argsort(distances)
        match_bool = self.labels == self.labels[index]
        return match_bool[sorted_index]

    def normalize_top_k_dict(self):
        for key, value in self.top_k.items():
            self.top_k[key] = value / self.prediction.shape[0]
        return self.top_k


class VAETopKAccuracy(TopKAccuracy):
    def get_prediction(self):
        _, _, prediction = self.model.predict(self.dataset)
        return prediction


if __name__ == "__main__":
    metadata_file = "simple_conv2d.meta"
    metadata = load_metadata(metadata_file)
    ip = InstructionParser(metadata["instruction"], is_dict=True)
    model = load_model_from_metadata(metadata_file)

    path_to_df = metadata["instruction"]["validation_data"]["dataframe"]
    validation_dataframe = load_dataframe(path_to_df)
    factory = FlatDatasetFactory(validation_dataframe, preprocessor=ip.model_factory.preprocessor())
    dataset = factory.get_dataset()

    topk_loop = TopKAccuracy(model, dataset, distance_metric="angular")
    print(topk_loop.get_top_k_accuracies(k_list=[1, 5, 10]))
