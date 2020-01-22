"""
Percentile
==========

A percentile is the value of a variable below which a certain percent of
observations fall.
The term percentile and the related term percentile rank are often used in
the reporting of scores from *normal-referenced tests*, 16th and 84th
percentiles corresponding to the 1-sigma interval of a Normal distribution.

Note that there are very common percentiles values:
    * 0th   = minimum value
    * 50th  = median value
    * 100th = maximum value


Weighted percentile
-------------------

A weighted percentile where the percentage in the total weight is counted
instead of the total number. *There is no standard function* for a weighted
percentile.

Implementation
--------------

The method implemented here extends the commom percentile estimation method
(linear interpolation beteeen closest ranks) approach in a natural way.
Suppose we have positive weights, W= [W_i], associated, respectively, with
our N sorted sample values, D=[d_i]. Let S_n = Sum_i=0..n {w_i} the
the n-th partial sum of the weights. Then the n-th percentile value is
given by the interpolation between its closest values v_k, v_{k+1}:

    v = v_k + (p - p_k) / (p_{k+1} - p_k) * (v_{k+1} - v_k)

where
    p_n = 100/S_n * (S_n - w_n/2)

Note that the 50th weighted percentile is known as the weighted median.


:author: MF
:last update: Thu Jun 13 11:29:47 PDT 2013
"""
import numpy as np



def percentile(data, percentiles, weights=None):
    """Compute weighted percentiles.

    If the weights are equal, this is the same as normal percentiles.
    Elements of the data and wt arrays correspond to each other and must have
    equal length.
    If wt is None, this function calls numpy's percentile instead (faster)

    TODO: re-implementing the normal percentile could be faster
          because it would avoid more variable checks and overheads

    Note: uses Cython code if available.

    INPUTS:
    -------
    data: ndarray[float, ndim=1]
        data points
    percentiles: ndarray[float, ndim=1]
        percentiles to use. (between 0 and 100)

    KEYWORDS:
    --------
    weights: ndarray[float, ndim=1] or None
        Weights of each point in data
        All the weights must be non-negative and the sum must be
        greater than zero.

    OUTPUTS:
    -------
    the weighted percentiles of the data.
    """
    # check if actually weighted percentiles is needed
    if weights is None:
        return np.percentile(data, list(percentiles))
    if np.equal(weights, 1.0).all():
        return np.percentile(data, list(percentiles))

    # make sure percentiles are fractions between 0 and 1
    if not np.greater_equal(percentiles, 0.0).all():
        raise ValueError("Percentiles less than 0")
    if not np.less_equal(percentiles, 100.0).all():
        raise ValueError("Percentiles greater than 100")

    # Make sure data is in correct shape
    shape = np.shape(data)
    n = len(data)
    if len(shape) != 1:
        raise ValueError("wrong data shape, expecting 1d")

    if len(weights) != n:
        print(n, len(weights))
        raise ValueError("weights must be the same shape as data")
    if not np.greater_equal(weights, 0.0).all():
        raise ValueError("Not all weights are non-negative.")

    _data = np.asarray(data, dtype=float)

    if hasattr(percentiles, "__iter__"):
        _p = np.asarray(percentiles, dtype=float) * 0.01
    else:
        _p = np.asarray([percentiles * 0.01], dtype=float)

    _wt = np.asarray(weights, dtype=float)

    
    isort = np.argsort(_data)
    sd = _data[isort]
    sw = _wt[isort]
    aw = np.cumsum(sw)

    if not aw[-1] > 0:
        raise ValueError("Nonpositive weight sum")

    w = (aw - 0.5 * sw) / np.sum(sw)
    o = np.interp(_p,w,sd)

    return o

    

def expectation(q, weights=None):
    """
    the expectation (or expected value or first moment) refers, to the value of
    a random variable one would "expect" to find if one could repeat the random
    variable process an infinite number of times and take the average of the
    values obtained.
    Formally, the expected value is a probability weighted average of all
    possible values.

    i.e.:
            integral(p(q) * q dq) / integral(p(q) dq),
    which in a discrete world becomes
            sum(p(q[i]) * q[i] / sum(p(q[i]))


    INPUTS
    ------
    q: ndarray[float, ndim=1]
        data from which we compute the expectation value
    wt: ndarray[float, ndim=1]
        weights associated to each data point

    OUTPUTS
    -------
    e: float
        expectation value

    NOTE
    -------
    (1) This function is about 30% fater than usning numpy.average
        to compute expectation values -- test by Yumi Choi on 1/17/2020
    """
    n = len(q)

    if weights is None:
        return np.mean(q)
    if np.equal(weights, 1.0).all():
        return np.mean(q)
    _w = np.asarray(weights, dtype=float)
    _q = np.asarray(q, dtype=float)
    e = (_q * _w).sum() / _w.sum()

    return e
