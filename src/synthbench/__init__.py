"""SynthBench — open benchmark harness for synthetic survey respondent quality."""

from synthbench.convergence.baseline import (
    BaselineGatedError,
    BaselineUnavailable,
    load_convergence_baseline,
)

__version__ = "0.1.0"

__all__ = [
    "BaselineGatedError",
    "BaselineUnavailable",
    "load_convergence_baseline",
    "__version__",
]
