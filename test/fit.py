from importlib import import_module

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import datasets
from sklearn_evaluation import plot

# parameters
model_type = 'sklearn.ensemble.RandomForestClassifier'
n_estimators = 5
criterion = 'gini'
max_depth= 10

X, y = datasets.make_classification(n_samples=10000,
                                    n_features=20,
                                    n_informative=5,
                                    n_classes=2,
                                    flip_y=0.1,
                                    class_sep=0.5,
                                    random_state=42)

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.33,
                                                    random_state=42)

module, _, attribute = model_type.rpartition('.')
class_ = getattr(import_module(module), attribute)

clf = class_(n_estimators=n_estimators,
             criterion=criterion,
             max_depth=max_depth)

print("Fitting model...")
_ = clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
y_score = clf.predict_proba(X_test)

cr = classification_report(y_test, y_pred, output_dict=True)

accuracy = accuracy_score(y_test, y_pred)
accuracy

precision = cr['1']['precision']
precision

recall = cr['1']['recall']
recall

f1 = cr['1']['f1-score']
f1

plot.confusion_matrix(y_test, y_pred)

plot.classification_report(y_test, y_pred)

plot.precision_recall(y_test, y_score)
