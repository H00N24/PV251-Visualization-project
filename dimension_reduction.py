#!/usr/bin/env python3
import os
from itertools import chain

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler
from umap import UMAP

from IA080_classifiers_comparison.src.data_loader import DataLoader

data_loader = DataLoader()
metal_data_generator = data_loader.get_metal_data(
    "IA080_classifiers_comparison/data/metal-data/", ""
)
exra_data_generator = data_loader.get_metal_data(
    "IA080_classifiers_comparison/data/extra-data/", ""
)

save_dir = "data/"

tsne = TSNE()
umap = UMAP()
pca = PCA(n_components=2)
scaler = MinMaxScaler()

for data_file_path, X, y, n_classes in chain(metal_data_generator, exra_data_generator):
    print(data_file_path, X.shape)

    small_frame = pd.DataFrame(X).sample(min(1000, X.shape[0]))

    X = small_frame.values
    y = y[small_frame.index]

    tsne_data = tsne.fit_transform(X)
    umap_data = umap.fit_transform(X)
    pca_data = pca.fit_transform(X)

    conc_data = np.concatenate((tsne_data, umap_data, pca_data), axis=1)

    scaled_data = scaler.fit_transform(conc_data).reshape(-1, 2)

    transformed_dataframe = pd.DataFrame(scaled_data, columns=("X", "Y"))

    transformed_dataframe["Class"] = np.repeat(y, 3)
    transformed_dataframe["Method"] = ["t-SNE", "UMAP", "PCA"] * y.shape[0]

    save_name = os.path.join(save_dir, data_file_path.replace(".data", "") + ".csv")

    transformed_dataframe.to_csv(save_name)
