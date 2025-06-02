import sys

import slingshot._databricks
from slingshot._databricks import (
    apply_project_recommendation,
    get_cluster,
    get_project_cluster,
    get_project_cluster_settings,
    get_project_job,
    get_recommendation_job,
)

__all__ = [
    "apply_project_recommendation",
    "get_cluster",
    "get_project_cluster",
    "get_project_cluster",
    "get_project_cluster_settings",
    "get_project_job",
    "get_recommendation_job",
]


if getattr(slingshot._databricks, "__claim", __name__) != __name__:
    # Unless building documentation you can't load both databricks modules in the same program
    if not sys.argv[0].endswith("sphinx-build"):
        raise RuntimeError(
            "Databricks modules for different cloud providers cannot be used in the same context"
        )

setattr(slingshot._databricks, "__claim", __name__)
