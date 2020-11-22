import os
import sys
import zipfile
import os.path as osp
import numpy as np

from typing import Optional, List, Tuple, Union, Callable
from graphgallery.data import Dataset
from graphgallery.data.io import makedirs, files_exist, download_file
from graphgallery.data.graph import Graph, load_dataset


_DATASETS = ('citeseer', 'citeseer_full', 'cora', 'cora_ml',
             'cora_full', 'amazon_cs', 'amazon_photo',
             'coauthor_cs', 'coauthor_phy', 'polblogs', 'karate_club',
             'pubmed', 'flickr', 'blogcatalog', 'dblp', 'acm', 'uai')

Transform = Union[List, Tuple, str, List, Tuple, Callable]


class NPZDataset(Dataset):

    github_url = "https://raw.githubusercontent.com/EdisonLeeeee/GraphData/master/datasets/{}.npz"
    supported_datasets = _DATASETS

    def __init__(self, name: str,
                 root: Optional[str] = None,
                 url: Optional[str] = None,
                 transform: Optional[Transform] = None,
                 verbose: bool = True
                 ):

        name = str(name)
        if not name in self.supported_datasets:
            print(f"Dataset not found in supported datasets. Using custom dataset: {name}.", file=sys.stderr)
            custom = True
        else:
            custom = False

        super().__init__(name, root, transform, verbose)

        self._url = url
        self.download_dir = self.root

        if not custom:
            makedirs(self.download_dir)
            self.download()
        elif not osp.exists(self.raw_paths[0]):
            raise RuntimeError(f"Dataset file '{name}' not exists. Please put the file in {self.raw_paths[0]}")

        self.process()

    def download(self) -> None:

        if files_exist(self.raw_paths):
            if self.verbose:
                print(f"Dataset {self.name} have already existed.")
                self.print_files(self.raw_paths)
            return

        self.print_files(self.raw_paths)

        if self.verbose:
            print("Downloading...")
        download_file(self.raw_paths, self.urls)
        if self.verbose:
            self.print_files(self.raw_paths)
            print("Downloading completed.")

    def process(self) -> None:
        if self.verbose:
            print("Processing...")
        graph = load_dataset(self.raw_paths[0])
#             self.raw_paths[0]).eliminate_selfloops().to_unweighted().to_undirected()
        # if self.standardize:
        #     graph = graph.standardize()
        self.graph = self.transform(graph)
        if self.verbose:
            print("Processing completed.")

    @property
    def url(self) -> str:
        if isinstance(self._url, str):
            return self._url
        else:
            return self.github_url.format(self.name)

    @property
    def raw_paths(self) -> List[str]:
        return [f"{osp.join(self.download_dir, self.name)}.npz"]
