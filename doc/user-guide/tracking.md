---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Experiment Tracking

```{important}
Experiment tracking requires ploomber-engine `0.0.11` or higher
```

+++

`ploomber-engine` comes with a tracker that allows you to log variables, and plots without modifying your code. A common use case is for managing Machine Learning experiments. However, you can use it for any other computational experiments where you want to record input parameters, outputs, and analyze results.

Under the hood, it uses the [`SQliteTracker`](https://sklearn-evaluation.readthedocs.io/en/latest/api/SQLiteTracker.html) from our [sklearn-evaluation](https://github.com/ploomber/sklearn-evaluation) package, this means that you will be able to query, and aggregate your experiments with SQL!

For this example, we'll train several Machine Learning models and evaluate their performance.

+++

## Dependencies

Before we run this example, we'll need to install the required dependencies:

```bash
pip install ploomber-engine sklearn-evaluation jupytext --upgrade
```

+++

Now, let's download the [sample script](https://github.com/ploomber/posts/blob/master/experiment-tracking/fit.py) we’ll use, Jupyter notebooks (`.ipynb`) are also supported:

```{code-cell} ipython3
%%sh
curl -O https://raw.githubusercontent.com/ploomber/posts/master/experiment-tracking/fit.py
```

Let's create our grid of parameters, we'll execute one experiment for each combination:

```{code-cell} ipython3
from ploomber_engine.tracking import track_execution
from sklearn.model_selection import ParameterGrid

grid = ParameterGrid(
    dict(
        n_estimators=[10, 15, 25, 50],
        model_type=["sklearn.ensemble.RandomForestClassifier"],
        max_depth=[5, 10, None],
        criterion=["gini", "entropy"],
    )
)
```

Let's now execute the script multiple times, one per set of parameters, and store the results in the `experiments.db` SQLite database:

```{code-cell} ipython3
for idx, p in enumerate(grid):
    if (idx + 1) % 10 == 0:
        print(f"Executed {idx + 1}/{len(grid)} so far...")

    track_execution("fit.py", parameters=p, quiet=True, database="experiments.db")
```

If you prefer so, you can also execute scripts from the terminal:

```bash
python -m ploomber_engine.tracking fit.py \
    -p n_estimators=100,model_type=sklearn.ensemble.RandomForestClassifier,max_depth=10
```

+++

## No extra code needed

+++

If you look at the [script's source code](https://github.com/ploomber/posts/blob/master/experiment-tracking/fit.py), you'll see that there are no extra imports or calls to log the experiments, it's a vanilla Python script.

The tracker runs the code, and it logs everything that meets any of the following conditions:

+++

**1. A line that contains a variable name by itself**

```python
accuracy = accuracy_score(y_test, y_pred)
accuracy
```

**2. A line that calls a function with no variable assignment**

```python
plot.confusion_matrix(y_test, y_pred)
```

Note that logs happen in groups (not line-by-line). A group is defined as a contiguous set of lines delimited with line breaks:

```python
# first group
accuracy = accuracy_score(y_test, y_pred)
accuracy

# second group
plot.confusion_matrix(y_test, y_pred)
```

Regular Python objects are supported (numbers, strings, lists, dictionaries), and any object with a rich representation will also work (e.g., matplotlib charts).

+++

## Querying experiments with SQL

+++

After finishing executing the experiments, we can initialize our database (`experiments.db`) and explore the results:

```{code-cell} ipython3
from sklearn_evaluation import SQLiteTracker

tracker = SQLiteTracker("experiments.db")
```

Since this is a SQLite database, we can use SQL to query our data using the `.query` method. By default, we get a `pandas.DataFrame`:

```{code-cell} ipython3
df = tracker.query(
    """
SELECT *
FROM experiments
LIMIT 5
"""
)

type(df)
```

```{code-cell} ipython3
df.head(3)
```

The logged parameters are stored in the `parameters` column. This column is a JSON object, and we can inspect the JSON keys with the `.get_parameters_keys()` method:

```{code-cell} ipython3
tracker.get_parameters_keys()
```

To get a sample query, we can use the `.get_sample_query()` method:

```{code-cell} ipython3
print(tracker.get_sample_query())
```

Let’s perform a simple query that extracts our metrics, sorts by F1 score, and returns the top three experiments:

```{code-cell} ipython3
tracker.query(
    """
SELECT
    uuid,
    json_extract(parameters, '$.f1') as f1,
    json_extract(parameters, '$.accuracy') as accuracy,
    json_extract(parameters, '$.criterion') as criterion,
    json_extract(parameters, '$.n_estimators') as n_estimators,
    json_extract(parameters, '$.precision') as precision,
    json_extract(parameters, '$.recall') as recall
FROM experiments
ORDER BY f1 DESC
LIMIT 3
""",
    as_frame=False,
    render_plots=False,
)
```

## Rendering plots

+++

Plots are essential for evaluating our analysis, and the experiment tracker can log them automatically. So let's pull the top 2 experiments (by F1 score) and get their confusion matrices, precision-recall curves, and classification reports. Note that we passed `as_frame=False` and `render_plots=True` to the `.query` method:

```{code-cell} ipython3
top_two = tracker.query(
    """
SELECT
    uuid,
    json_extract(parameters, '$.f1') as f1,
    json_extract(parameters, '$.confusion_matrix') as confusion_matrix,
    json_extract(parameters, '$.precision_recall') as precision_recall,
    json_extract(parameters, '$.classification_report') as classification_report
FROM experiments
ORDER BY f1 DESC
LIMIT 2
""",
    as_frame=False,
    render_plots=True,
)

top_two
```

## Comparing plots

+++

If you want to zoom into a couple of experiment plots, you can select one and create a tab view. First, let's retrieve the confusion matrices from the top 2 experiments:

```{code-cell} ipython3
top_two.get("confusion_matrix")
```

The buttons in the top bar allow us to switch between the two plots of the selected experiments. We can do the same with the precision-recall curve:

```{code-cell} ipython3
top_two.get("precision_recall")
```

Note that the tabs will take the value of the first column in our query (in our case, the experiment ID). So let's switch them to show the F1 score via the `index_by` argument:

```{code-cell} ipython3
top_two.get("classification_report", index_by="f1")
```

## Aggregation and plotting

+++

Using SQL gives us power and flexibility to answer sophisticated questions about our experiments.

For example, let's say we want to know the effect of the number of trees (`n_estimators`) on our metrics. We can quickly write a SQL that aggregates by `n_estimators` and computes the mean of all our metrics; then, we can plot the values.

First, let's run the query. Note that we're passing `as_frame=True` so we get a `pandas.DataFrame` we can manipulate:

```{code-cell} ipython3
df = tracker.query(
    """
SELECT
    json_extract(parameters, '$.n_estimators') as n_estimators,
    AVG(json_extract(parameters, '$.accuracy')) as accuracy,
    AVG(json_extract(parameters, '$.precision')) as precision,
    AVG(json_extract(parameters, '$.recall')) as recall,
    AVG(json_extract(parameters, '$.f1')) as f1
FROM experiments
GROUP BY n_estimators
""",
    as_frame=True,
).set_index("n_estimators")

df
```

Now, let's create the plot:

```{code-cell} ipython3
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

for metric in ["accuracy", "f1", "recall", "precision"]:
    df[metric].plot(ax=ax, marker="o", style="--")

ax.legend()
ax.grid()
ax.set_title("Effect of increasing n_estimators")
ax.set_ylabel("Metric")
_ = ax.set_xticks(df.index)
```

We can see that increasing `n_estimators` drives our metrics up; however, after 25 estimators, the improvements get increasingly small. Considering that a larger number of `n_estimators` will increase the runtime of each experiment, we can use this plot to inform our following experiments, cap `n_estimators`, and focus on other parameters.

+++

If you need more details on how to work with the `SQLiteTracker`, you cna jump directly to the [full example in the documentation](https://sklearn-evaluation.readthedocs.io/en/latest/user_guide/SQLiteTracker.html).
