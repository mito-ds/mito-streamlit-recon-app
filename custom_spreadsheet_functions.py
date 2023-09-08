from fuzzywuzzy import fuzz
import pandas as pd

MATCH = 'Match'
IMMATERIAL = 'Immaterial'
FAIL = 'Fail'


def CHECK_NUMBER_DIFFERENCE(series_one, series_two, tolerance=0.0):
    """
    {
        "function": "CHECK_NUMBER_DIFFERENCE",
        "description": "Returns 'Match' if the two columns are exactly equal, 'Immaterial' if the two columns are within the tolerance, and the difference otherwise.",
        "search_terms": ["check", "number", "difference", "tolerance"],
        "examples": [
            "CHECK_NUMBER_DIFFERENCE(excel, db, 0.5)"
        ],
        "syntax": "CHECK_NUMBER_DIFFERENCE(number_column_one, number_column_two, tolerance)",
        "syntax_elements": [
            {
                "element": "number_column_one",
                "description": "The first number column to compare."
            },
            {
                "element": "number_column_two",
                "description": "The second number column to compare."
            },
            {
                "element": "tolerance",
                "description": "Differences less than the tolerance will be labeled immaterial."
            }
        ]
    }
    """

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
    """
    {
        "function": "CHECK_STRING_DIFFERENCE",
        "description": "Returns 'Match' if the two columns are exactly equal, 'Immaterial' if the two columns's similarity are greater than the tolerance, and the similarity of the strings otherwise.",
        "search_terms": ["check", "string", "difference", "tolerance"],
        "examples": [
            "CHECK_STRING_DIFFERENCE(excel, db, 90)"
        ],
        "syntax": "CHECK_STRING_DIFFERENCE(string_column_one, string_column_two, similarity_threshold)",
        "syntax_elements": [
            {
                "element": "string_column_one",
                "description": "The first string column to compare."
            },
            {
                "element": "string_column_two",
                "description": "The second string column to compare."
            },
            {
                "element": "similarity_threshold",
                "description": "The minimum required similarity between the two strings. Two identical strings have a similarity of 100."
            }
        ]
    }
    """

    def label_fuzzy_ratio(value1, value2, similarity_threshold):
        ratio = fuzz.ratio(str(value1), str(value2))

        if ratio == 100:
            return 'Match'
        if ratio > similarity_threshold:
            return 'Immaterial'
        return ratio

    return pd.Series([label_fuzzy_ratio(val1, val2, similarity_threshold) for val1, val2 in zip(series_one, series_two)], index=series_one.index)

