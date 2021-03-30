from src.instruction_utility import *
import tensorflow as tf
from PIL import Image
import numpy as np

import base64, io


def convert_base64_string_to_array(base64_string):
    decoded = base64.b64decode(base64_string.split(",")[1])
    bytes_image = io.BytesIO(decoded)
    image = Image.open(bytes_image, formats=None).convert('RGB')
    return np.array(image)


def distance(vec1, vec2, metric="L2"):
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()
    vec1 = normalize_vector(vec1)
    vec2 = normalize_vector(vec2)

    if metric == "L2":
        return np.linalg.norm((vec1 - vec2))
    if metric == "angular":
        return np.maximum(1. - np.dot(vec1, vec2), 0.0)


def normalize_vector(vec):
    return vec / np.linalg.norm(vec)


class ModelInference:
    def __init__(self, metafile):
        self.model = load_model_from_metadata(metafile)
        self.metadata = load_metadata(metafile)
        self.preprocessor, self.input_shape = self.get_model_specifics()

    def get_model_specifics(self):
        ip = InstructionParser(self.metadata["instruction"], is_dict=True)
        return ip.model_factory.preprocessor(), ip.model_factory.input_shape

    def predict(self, base64_string):
        array = convert_base64_string_to_array(base64_string)
        image = tf.expand_dims(array, 0)
        image = tf.image.resize(image, [self.input_shape[0], self.input_shape[1]])
        return np.array(self.model.predict(image))

    def get_metric(self):
        return self.model.loss._fn_kwargs["distance_metric"]


if __name__ == "__main__":
    im = Image.open("/home/sascha/camara_data/IMG_20210324_154137.jpg")
    array = np.array(im)

    model = ModelInference("simple_conv2d_embedding_size_16.meta")
    print(model.predict(array))
