from fuzzywuzzy import fuzz
import pandas as pd

MATCH = 'Match'
IMMATERIAL = 'Immaterial'
FAIL = 'Fail'


def CHECK_NUMBER_DIFFERENCE(series_one, series_two, tolerance=0.0):
    # If the difference between the columns is more than number_difference_tolerance, then display the difference, otherwise label it immaterial

    # Calculate the difference between the two series
    diff_series = series_one - series_two

    def label_difference(diff, tolerance):
        if diff == 0:
            return 'Match'
        if abs(diff) < tolerance:
            return 'Immaterial'
        return diff

    # Create a new column based on the tolerance
    return diff_series.apply(lambda diff: label_difference(diff, tolerance))


def CHECK_STRING_DIFFERENCE(series_one, series_two, similarity_threshold=100):

    def label_fuzzy_ratio(value1, value2, similarity_threshold):
        ratio = fuzz.ratio(str(value1), str(value2))

        if ratio == 100:
            return 'Match'
        if ratio > similarity_threshold:
            return 'Immaterial'
        return ratio

    return pd.Series([label_fuzzy_ratio(val1, val2, similarity_threshold) for val1, val2 in zip(series_one, series_two)], index=series_one.index)

