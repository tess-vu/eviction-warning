import numpy as np

def mean_signed_error(y_true, y_pred):
    """mean(predicted - observed): positive = over-prediction, negative = under-prediction."""
    return float(np.mean(np.asarray(y_pred) - np.asarray(y_true)))

def mean_observed(y_true, y_pred):
    """Mean of observed values (y_true)."""
    return float(np.mean(np.asarray(y_true)))

def mean_predicted(y_true, y_pred):
    """Mean of predicted values (y_pred)."""
    return float(np.mean(np.asarray(y_pred)))
