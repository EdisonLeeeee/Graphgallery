from graphgallery.nn.gallery import SemiSupervisedModel
from graphgallery.nn.models.pyg import GCN as pygGCN
from graphgallery.sequence import FullBatchNodeSequence
from graphgallery import functional as F

class GCN(SemiSupervisedModel):

    def __init__(self, *graph, adj_transform="normalize_adj", attr_transform=None,
                 device='cpu:0', seed=None, name=None, **kwargs):
        """
        Initialize the graph.

        Args:
            self: (todo): write your description
            graph: (todo): write your description
            adj_transform: (todo): write your description
            attr_transform: (todo): write your description
            device: (todo): write your description
            seed: (int): write your description
            name: (str): write your description
        """
        super().__init__(*graph, device=device, seed=seed, name=name, **kwargs)

        self.adj_transform = F.get(adj_transform)
        self.attr_transform = F.get(attr_transform)
        self.process()

    def process_step(self):
        """
        Process the adjacency matrix.

        Args:
            self: (todo): write your description
        """
        graph = self.graph
        adj_matrix = self.adj_transform(graph.adj_matrix)
        attr_matrix = self.attr_transform(graph.attr_matrix)
        edge_index, edge_weight = F.sparse_adj_to_edge(adj_matrix)

        self.feature_inputs, self.structure_inputs = F.astensors(
            attr_matrix, (edge_index, edge_weight), device=self.device)

    # use decorator to make sure all list arguments have the same length
    @F.EqualVarLength()
    def build(self, hiddens=[16], activations=['relu'], dropout=0.5,
              l2_norm=5e-4, lr=0.01, use_bias=True):
        """
        Constructs the hiddar graph

        Args:
            self: (todo): write your description
            hiddens: (int): write your description
            activations: (todo): write your description
            dropout: (bool): write your description
            l2_norm: (todo): write your description
            lr: (todo): write your description
            use_bias: (bool): write your description
        """

        self.model = pygGCN(self.graph.n_attrs, self.graph.n_classes, hiddens=hiddens,
                           activations=activations, dropout=dropout, l2_norm=l2_norm,
                           lr=lr, use_bias=use_bias).to(self.device)

    def train_sequence(self, index):
        """
        Train a batch of features.

        Args:
            self: (todo): write your description
            index: (int): write your description
        """
        
        labels = self.graph.labels[index]
        sequence = FullBatchNodeSequence(
            [self.feature_inputs, *self.structure_inputs, index], labels, device=self.device)
        return sequence
