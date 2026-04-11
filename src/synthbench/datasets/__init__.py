from synthbench.datasets.base import Dataset, Question
from synthbench.datasets.opinionsqa import OpinionsQADataset
from synthbench.datasets.globalopinionqa import GlobalOpinionQADataset
from synthbench.datasets.subpop import SubPOPDataset

DATASETS: dict[str, type[Dataset]] = {
    "opinionsqa": OpinionsQADataset,
    "globalopinionqa": GlobalOpinionQADataset,
    "subpop": SubPOPDataset,
}

__all__ = [
    "Dataset",
    "Question",
    "OpinionsQADataset",
    "GlobalOpinionQADataset",
    "SubPOPDataset",
    "DATASETS",
]
