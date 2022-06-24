import random
import logging
import numpy as np

__version__ = "1.6.0"
logger = logging.getLogger(__name__)

class Router(object):
    """ Seldon Router to handle multi-handed (arbitrary number of models) A/B test
    ----------
    n_branches : int
        Number of child components/models the router will route requests to
    verbose : bool
        Set the logger level
    seed : int, optional
        Set the random seed
    history : bool
        Set storing router history
    branch_names: str, optional
        A string specifying branch names separated by `:`
    branch_probabilities : float
        Float numbers specifying the probability of choosing each branch separated by `:`
    """

    def __init__(
        self,
        n_branches=None,
        verbose=False,
        seed=None,
        history=False,
        branch_names=None,
        branch_probabilities=None
    ):

        if verbose:
            logger.setLevel(10)
            logger.info("Enabling debug mode")

        logger.info(f"Starting { __name__} Microservice, version {__version__}")

        # for reproducibility
        if seed:
            logger.info("Setting random seed to %s", seed)
            random.seed(seed)
            np.random.seed(seed)

        try:
            n_branches = int(n_branches)
            assert n_branches > 0
        except (TypeError, ValueError, AssertionError):
            logger.exception("n_branches parameter must be given")
            raise

        self.name = __name__ + __version__
        self.verbose = verbose
        self.n_branches = n_branches
        self.history = history

        self.branch_success = [0 for _ in range(n_branches)]
        self.branch_tries = [0 for _ in range(n_branches)]
        self.branch_values = [0 for _ in range(n_branches)]

        if self.history:
            logger.info("Enabling history")
            self.branch_history = []

        if branch_names is not None:
            self.branch_names = branch_names.split(":")
            logger.info("Branch names: %s", self.branch_names)

        if branch_probabilities is not None:
            self.branch_probabilities = [float(x) for x in branch_probabilities.split(":")]
            self.branch_probabilities = [x / sum(self.branch_probabilities) for x in self.branch_probabilities]
            logger.info("Branch probabilities: %s", self.branch_probabilities)

        try:
            assert self.n_branches == len(self.branch_names)
            assert self.n_branches == len(self.branch_probabilities)
            assert np.isclose(sum(self.branch_probabilities), 1)
        except (TypeError, ValueError, AssertionError):
            logger.exception("invalid branch parameters")
            raise

        logger.info(
            f"Router initialised, n_branches: {self.n_branches}, {self.branch_names}, {self.branch_probabilities}"
        )

    def route(self, features, feature_names):
        logger.info("Routing features %s, %s", features, feature_names)

        selected_branch_id = np.random.choice(
            range(self.n_branches),
            size=1,
            replace=False,
            p=self.branch_probabilities
        )[0]

        if self.history:
            self.branch_history.append(selected_branch_id)

        logger.debug("Routing to branch %s", selected_branch_id)
        return int(selected_branch_id)
