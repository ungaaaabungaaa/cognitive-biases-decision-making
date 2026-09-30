"""cogbias: models, simulations and experiments on cognitive biases in decision-making.

The package has four layers:

* :mod:`cogbias.catalogue`  - a curated, referenced catalogue of biases.
* :mod:`cogbias.models`     - formal (quantitative) models of individual biases.
* :mod:`cogbias.simulation` - agent-based simulations that reproduce classic findings.
* :mod:`cogbias.analysis`   - statistics that measure a bias in real or simulated data.
* :mod:`cogbias.debiasing`  - interventions and how much they help, in the same models.
"""

from cogbias.catalogue import BIASES, Bias, get_bias
from cogbias.models import (
    prospect_value,
    probability_weight,
    prospect_utility,
    anchored_estimate,
    bayesian_update,
    confirmation_biased_update,
    base_rate_neglect_posterior,
    choice_probability,
)

__version__ = "0.1.0"

__all__ = [
    "BIASES",
    "Bias",
    "get_bias",
    "prospect_value",
    "probability_weight",
    "prospect_utility",
    "anchored_estimate",
    "bayesian_update",
    "confirmation_biased_update",
    "base_rate_neglect_posterior",
    "choice_probability",
]
