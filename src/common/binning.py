"""
Holds the functions for binning the dataset by age.
"""
import numpy as np

BIN_LABELS = ["All", "Bin 1", "Bin 2", "Bin 3"]
ONLY_BIN_LABELS = ["Bin 1", "Bin 2", "Bin 3"]
EQUAL_BIN_LABELS = ["Bin 1", "Bin 2 Equal", "Bin 3"]


def get_age_bins_indices(ages, num_bins):
    """
    Gets the indices that bins the participant by age.

    This does not return the samples binned by age, but the age bins
    containing indices of samples. To actually bin the data by age, use the
    list returned by this function and index the samples or use bin_by_age().

    Parameters
    ----------
    ages : np.array
        List of participant ages.
    num_bins : int
        Number of age bins.

    Returns
    -------
    bin_indices : list
        List where the length is num_bins and each element is a list of
        indices for each age bin.

    """
    bin_indices = []

    if num_bins == 3:
        bin_1 = np.where(ages <= 9)
        bin_2 = np.where(np.logical_and(9 < ages, ages <= 12))
        bin_3 = np.where(12 < ages)
        bin_indices = [bin_1, bin_2, bin_3]
    elif num_bins == 2:
        bin_1 = np.where(ages <= 10)
        bin_2 = np.where(10 < ages)
        bin_indices = [bin_1, bin_2]

    return bin_indices


def bin_by_age(X, y, ages, num_bins):
    """
    Bins the data by age.

    Parameters
    ----------
    X : np.array
    y : np.array
    ages : np.array
    num_bins : int

    Returns
    -------
    bins: list
        List where it's length is equal to the number of age bins and each
        element is a list of tuples containing the samples and targets for
        that age bin.

    Notes
    -----
    Typically bins the data into three age bins: 6-8, 9-11, and 12-16.

    """
    bin_indices = get_age_bins_indices(ages, num_bins)

    if y.ndim == 1:
        bins = [(X[bin_index], y[bin_index]) for bin_index in bin_indices]
    else:
        bins = [(X[bin_index], y[bin_index, :]) for bin_index in bin_indices]

    return bins


def bin_data(X, y, ages=None, include_all=False, num_bins=3):
    """
    Bins the data by age or returns the original data.

    Used to wrap the bin_by_age() function when running multiple modeling
    sessions.

    Parameters
    ----------
    X : np.array
    y : np.array
    ages : np.array, optional
    include_all : bool, optional
    num_bins : int, optional

    Returns
    -------
    tuple
        A tuple containing the samples, targets, and bin labels

    """
    if ages is not None and ages.any():
        bins = bin_by_age(X, y, ages, num_bins)

        X_bins, y_bins, bin_labels = [], [], []

        if include_all:
            X_bins.append(X)
            y_bins.append(y)
            bin_labels.append('All')

        for bin_num, age_bin in enumerate(bins, start=1):
            X_bins.append(age_bin[0])
            y_bins.append(age_bin[1])
            bin_labels.append(f'Bin {bin_num}')

    else:
        X_bins = [X]
        y_bins = [y]
        bin_labels = ["All"]

    return (np.array(X_bins, dtype=object), np.array(y_bins, dtype=object),
            np.array(bin_labels, dtype=object))


def subsample_bin(X_bin, y_bin, num_samples):
    """
    Subsamples an age bin randomly for the given number of samples.
    
    Parameters
    ----------
    X_bin : np.array
    y_bin : np.array
    num_samples : int

    Returns
    -------
    tuple
        A tuple containing the subsampled X and y
    
    """
    subsample_indices = np.random.choice(X_bin.shape[0], num_samples, replace=False)
    
    return X_bin[subsample_indices], y_bin[subsample_indices]


def bin_by_sliding_window(X: np.array, y: np.array, ages: np.array, window_size: int = 3):
    """Bins the data by a sliding age window.

    Parameters
    ----------
    X
    y
    ages
    window_size

    Returns
    -------

    """
    all_sliding_windows = []
    age_windows = []
    min_age, max_age = int(np.round(np.min(ages))), int(np.round(np.max(ages)))

    for current_window in range(min_age, max_age - window_size):
        if current_window == 12:
            min_window_age, max_window_age = current_window, current_window + window_size
        else:
            min_window_age, max_window_age = current_window, current_window + window_size - 1
        
        window_indices = np.where(np.logical_and(min_window_age <= ages, ages <= max_window_age))
        X_window, y_window = X[window_indices], y[window_indices]
        all_sliding_windows.append((X_window, y_window))
        age_windows.append((min_window_age, max_window_age))

    return all_sliding_windows, age_windows


def bin_by_random_equivalent_size(X, y, bin_sizes=(114, 147, 112)) -> tuple:
    """Bins the data into equivalent sized bins, disregarding age.

    Parameters
    ----------
    X
    y
    bin_sizes

    Returns
    -------

    """
    X_bins, y_bins, bin_labels = [], [], []
    random_indices = np.random.choice(X.shape[0], X.shape[0], replace=False)
    bin_indices = [random_indices[0:bin_sizes[0]], random_indices[bin_sizes[0]:bin_sizes[0]+bin_sizes[1]], random_indices[bin_sizes[1]:bin_sizes[1]+bin_sizes[2]]]

    for bin_num, bin_index in enumerate(bin_indices, start=1):
        X_bins.append(X[bin_index])
        y_bins.append(y[bin_index])
        bin_labels.append(f'Bin {bin_num}')

    return X_bins, y_bins, bin_labels


def bin_to_approximate_size(X, y, N=75):
    if len(X) < N:
        return X, y

    random_indices = np.random.choice(X.shape[0], N, replace=False)
    return X[random_indices], y[random_indices]
