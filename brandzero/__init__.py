"""Brand Zero -- the 31st brand: the one that ships no product and holds
everything the other 30 have learned."""

from .schema import Claim, Prediction, DECISION_CLASSES, EVIDENCE_TIERS
from .model import HierarchicalPrior, naive_pool
from .allocator import PortfolioAllocator, Experiment, expected_opportunity_loss
from .calibration import CalibrationLedger, model_forecast
from .backtest import hold_one_brand_out, format_report

__all__ = [
    "Claim", "Prediction", "DECISION_CLASSES", "EVIDENCE_TIERS",
    "HierarchicalPrior", "naive_pool",
    "PortfolioAllocator", "Experiment", "expected_opportunity_loss",
    "CalibrationLedger", "model_forecast",
    "hold_one_brand_out", "format_report",
]
