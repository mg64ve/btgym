import numpy as np
from scipy.stats import norm
from .base import BaseCombinedDataSet, BasePairCombinedDataSet, base_spread_generator_fn
from .utils import log_uniform


def weiner_process_fn(num_points, delta, x0=0, dt=1):
    """
    Generates Weiner process realisation trajectory.

    Args:
        num_points:     int, trajectory length;
        delta:          float, speed parameter;
        x0:             float, starting point;
        dt:             int, time increment;

    Returns:
        generated data as 1D np.array
    """
    x0 = np.asarray(x0)
    r = norm.rvs(size=x0.shape + (num_points,), scale=delta * (dt**.5))

    return np.cumsum(r, axis=-1) + np.expand_dims(x0, axis=-1)


def weiner_process_uniform_parameters_fn(delta, x0, dt=1):
    """
    Provides parameters for Weiner process.
    If parameter is set as iterable of form [a, b] - uniformly randomly samples parameters value
    form given interval.

    Args:
        delta:          float or iterable of 2 floats, speed parameter;
        x0:             float or iterable of 2 floats, starting point;

    Returns:

    """
    if type(delta) in [int, float, np.float64]:
        delta = [delta, delta]
    else:
        delta = list(delta)

    if type(x0) in [int, float, np.float64]:
        x0 = [x0, x0]
    else:
        x0 = list(x0)

    assert len(delta) == 2 and 0 <= delta[0] <= delta[-1], \
        'Expected Weiner delta be non-negative float or ordered interval, got: {}'.format(delta)

    assert len(x0) == 2 and 0 <= x0[0] <= x0[-1], \
        'Expected Weiner starting x0 be non-negative float or ordered interval, got: {}'.format(x0)

    delta_value = np.random.uniform(low=delta[0], high=delta[-1])
    x0_value = np.random.uniform(low=x0[0], high=x0[-1])

    return dict(
        delta=delta_value,
        x0=x0_value
    )


def ornshtein_uhlenbeck_process_fn(num_points, mu, l, sigma, x0=0, dt=1):
    """
    Generates Ornshtein-Uhlenbeck process realisation trajectory.

    Args:
        num_points:     int, trajectory length
        mu:             float, mean;
        l:              float, lambda, mean reversion rate;
        sigma:          float, volatility;
        x0:             float, starting point;
        dt:             int, time increment;

    Returns:
        generated data as 1D np.array
    """
    # print('OU_p_fn got:: l: {}, sigma: {}, mu: {}'.format(l, sigma, mu))

    n = num_points
    x = np.zeros(n)
    x[0] = x0
    for i in range(1, n):
        x[i] = x[i - 1] * np.exp(-l * dt) + mu * (1 - np.exp(-l * dt)) + \
               sigma * ((1 - np.exp(-2 * l * dt)) / (2 * l)) ** .5 * np.random.normal(0, 1)

    return x


def ornshtein_uhlenbeck_uniform_parameters_fn(mu, l, sigma, x0=None, dt=1):
    """
    Provides parameters for OU process.
    If parameter is set as iterable of form [a, b] - uniformly randomly samples parameters value
    form given interval.

    Args:
        mu:             float or iterable of 2 floats, mean;
        l:              float or iterable of 2 floats, lambda, mean reversion rate;
        sigma:          float or iterable of 2 floats, volatility;
        x0:             float or iterable of 2 floats, starting point;
        dt:             not used | int, time increment;

    Returns:
        dictionary of sampled values
    """
    if type(l) in [int, float, np.float64]:
        l = [l, l]
    else:
        l = list(l)

    if type(sigma) in [int, float, np.float64]:
        sigma = [sigma, sigma]
    else:
        sigma = list(sigma)

    if type(mu) in [int, float, np.float64]:
        mu = [mu, mu]
    else:
        mu = list(mu)

    # Sanity checks:
    assert len(l) == 2 and 0 < l[0] <= l[-1], \
        'Expected OU mean reversion rate be positive float or ordered interval, got: {}'.format(l)
    assert len(sigma) == 2 and 0 <= sigma[0] <= sigma[-1], \
        'Expected OU sigma be non-negative float or ordered interval, got: {}'.format(sigma)
    assert len(mu) == 2 and mu[0] <= mu[-1], \
        'Expected OU mu be float or ordered interval, got: {}'.format(mu)

    # Uniformly sample params:
    l_value = np.random.uniform(low=l[0], high=l[-1])
    sigma_value = np.random.uniform(low=sigma[0], high=sigma[-1])
    mu_value = np.random.uniform(low=mu[0], high=mu[-1])

    if x0 is None:
        # Choose starting point equal to mean:
        x0_value = mu_value

    else:
        if type(x0) in [int, float, np.float64]:
            x0 = [x0, x0]
        else:
            x0 = list(x0)

        assert len(x0) == 2 and x0[0] <= x0[-1], \
            'Expected OU x0 be float or ordered interval, got: {}'.format(x0)

        x0_value = np.random.uniform(low=x0[0], high=x0[-1])

    # print('OU_params_fn sample intervals:: l: {}, sigma: {}, mu: {}, x0: {}'.format(l, sigma, mu, x0))
    # print('OU_params_fn passed:: l: {}, sigma: {}, mu: {}, x0: {}'.format(l_value, sigma_value, mu_value, x0_value))

    return dict(
        l=l_value,
        sigma=sigma_value,
        mu=mu_value,
        x0=x0_value,
        #dt=dt
    )


def ornshtein_uhlenbeck_log_uniform_parameters_fn(mu, l, sigma, x0=None, dt=1):
    """
    Provides parameters for OU process.
    If `mu`, `sigma` is set as iterable of form [a, b] - uniformly randomly samples parameters value
    form given interval; `l` is sampled from log-uniform distribution


    Args:
        mu:             float or iterable of 2 floats, mean;
        l:              float or iterable of 2 floats, lambda, mean reversion rate;
        sigma:          float or iterable of 2 floats, volatility;
        x0:             float or iterable of 2 floats, starting point;
        dt:             not used | int, time increment;

    Returns:
        dictionary of sampled values
    """
    if type(l) in [int, float, np.float64]:
        l = [l, l]
    else:
        l = list(l)

    if type(sigma) in [int, float, np.float64]:
        sigma = [sigma, sigma]
    else:
        sigma = list(sigma)

    if type(mu) in [int, float, np.float64]:
        mu = [mu, mu]
    else:
        mu = list(mu)

    # Sanity checks:
    assert len(l) == 2 and 0 < l[0] <= l[-1], \
        'Expected OU mean reversion rate be positive float or ordered interval, got: {}'.format(l)
    assert len(sigma) == 2 and 0 <= sigma[0] <= sigma[-1], \
        'Expected OU sigma be non-negative float or ordered interval, got: {}'.format(sigma)
    assert len(mu) == 2 and mu[0] <= mu[-1], \
        'Expected OU mu be float or ordered interval, got: {}'.format(mu)

    # Uniformly sample params:
    l_value = log_uniform(l, 1)
    sigma_value = np.random.uniform(low=sigma[0], high=sigma[-1])
    mu_value = np.random.uniform(low=mu[0], high=mu[-1])

    if x0 is None:
        # Choose starting point equal to mean:
        x0_value = mu_value

    else:
        if type(x0) in [int, float, np.float64]:
            x0 = [x0, x0]
        else:
            x0 = list(x0)

        assert len(x0) == 2 and x0[0] <= x0[-1], \
            'Expected OU x0 be float or ordered interval, got: {}'.format(x0)

        x0_value = np.random.uniform(low=x0[0], high=x0[-1])

    # print('OU_params_fn sample intervals:: l: {}, sigma: {}, mu: {}, x0: {}'.format(l, sigma, mu, x0))
    # print('OU_params_fn passed:: l: {}, sigma: {}, mu: {}, x0: {}'.format(l_value, sigma_value, mu_value, x0_value))

    return dict(
        l=l_value,
        sigma=sigma_value,
        mu=mu_value,
        x0=x0_value,
        #dt=dt
    )


def coupled_wave_pair_generator_fn(
        num_points,
        drift_sigma,
        ou_sigma,
        ou_lambda,
        ou_mu,
        spread_sigma_1,
        spread_sigma_2,
        spread_mean_1,
        spread_mean_2,
        bias,
        keep_decimals=6,
):
    """
    Generates two integrated trajectories of OHLC prices.
    Prices are modelled by OU process with stochastic drift;
    High-Low spread values for each price line independently generated by 'coupled wave model',
    see  formulae (18a-c) - (20),  pp. 10-11 in:
    Jack Sarkissian, "Spread, volatility, and volume relationship in
    financial markets and market maker’s profit optimization",
    https://arxiv.org/pdf/1606.07381.pdf

    Args:
        num_points:         int, trajectory length
        drift_sigma:        ufloat, stichastic drift sigma
        ou_sigma:           ufloat, base OU process sigma
        ou_lambda:          ufloat, base OU mean-reverting speed parameter
        ou_mu:              float, base OU mean parameter
        spread_sigma_1:     ufloat, Hi-Lo spread generating sigma1
        spread_sigma_2:     ufloat, Hi-Lo spread generating sigma2
        spread_mean_1:      float, Hi-Lo spread generating mean1
        spread_mean_2:      float, Hi-Lo spread generating mean2
        bias:               ufloat, process starting point
        keep_decimals:      uint, number of decimal places to keep in generated data

    Returns:
        3d array of generated values of shape [2, 4, num_points]
    """
    # Price iteration by "coupled-wave model", formulae (18a-c) - (20),  pp. 10-11:
    s_mid = lambda s_last, sigma: s_last * (1 + np.random.normal(loc=0.0, scale=sigma, size=None))

    h = lambda sigma1, sigma2, mean1, mean2: np.clip((
        np.random.normal(loc=mean1, scale=sigma1, size=None) ** 2 +
        np.random.normal(loc=mean2, scale=sigma2, size=None) ** 2
         ) ** .5, mean1, None)

    s_low = lambda x_mid, h_val: x_mid - h_val / 2

    s_high = lambda x_mid, h_val: x_mid + h_val / 2

    s_last = lambda x_low, x_high: np.random.uniform(low=x_low, high=x_high, size=None)

    delta_ou = lambda s, l, sigma: (ou_mu - s) * (1 - np.exp(-l)) + sigma * (
                (1 - np.exp(-2 * l)) / (2 * l)) ** .5 * np.random.normal(0, 1)

    x_mid1 = [bias]
    x_low1 = [bias]
    x_high1 = [bias]
    x_last1 = [bias + ou_mu/2]
    x_mid2 = [bias]
    x_low2 = [bias]
    x_high2 = [bias]
    x_last2 = [bias - ou_mu/2]

    # Generate trajectory:
    for i in range(num_points):
        x_last_ou = (x_last1[-1] - x_last2[-1])

        d_s = delta_ou(x_last_ou, ou_lambda, ou_sigma)

        drift1 = np.random.normal(loc=0.0, scale=drift_sigma, size=None)
        #drift2 = np.random.normal(loc=0.0, scale=drift_sigma, size=None)

        x_mid1.append(x_last1[-1] * (1 + drift1) + d_s / 2)
        x_mid2.append(x_last2[-1] * (1 + drift1) - d_s / 2)

        #     dd = np.random.uniform(0,1)
        #     x_mid1.append(x_last1[-1] + d_s*(1-dd))
        #     x_mid2.append(x_last2[-1] - d_s*dd)

        h1_val = h(spread_sigma_1, spread_sigma_2, spread_mean_1, spread_mean_2)
        h2_val = h(spread_sigma_1, spread_sigma_2, spread_mean_1, spread_mean_2)

        x_low1.append(s_low(x_mid1[-1], h1_val))
        x_high1.append(s_high(x_mid1[-1], h1_val))
        x_last1.append(s_last(x_low1[-1], x_high1[-1]))

        x_low2.append(s_low(x_mid2[-1], h2_val))
        x_high2.append(s_high(x_mid2[-1], h2_val))
        x_last2.append(s_last(x_low2[-1], x_high2[-1]))

    x = np.asarray([[x_mid1, x_high1, x_low1, x_last1], [x_mid2, x_high2, x_low2, x_last2]])[:, :, 1:]

    return np.around(x, decimals=keep_decimals)