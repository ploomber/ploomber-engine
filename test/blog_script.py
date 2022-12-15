from ploomber_engine.tracking import track_execution
from sklearn.model_selection import ParameterGrid

grid = ParameterGrid(
    dict(
        n_estimators=[5, 10, 15, 25, 50, 100],
        model_type=["sklearn.ensemble.RandomForestClassifier"],
        max_depth=[5, 10, None],
        criterion=["gini", "entropy", "log_loss"],
    )
)

for idx, p in enumerate(grid):
    if (idx + 1) % 10 == 0:
        print(f"Executed {idx + 1}/{len(grid)} so far...")

    track_execution("fit.py", parameters=p, quiet=True, database="experiments.db")

