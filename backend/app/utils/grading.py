"""
Grading scale used across the Examination module.

Maps a percentage score to a letter grade and a GPA point (4.0 scale).
Kept in one place so the whole system (results, report cards, GPA calculation)
stays consistent if the school ever wants to tune the bands.
"""

from typing import Tuple

# (minimum percentage inclusive, letter grade, gpa points)
GRADE_BANDS = [
    (90, "A+", 4.0),
    (80, "A", 3.7),
    (70, "B", 3.3),
    (60, "C", 3.0),
    (50, "D", 2.0),
    (40, "E", 1.0),
    (0, "F", 0.0),
]


def calculate_grade(marks_obtained: float, total_marks: float) -> Tuple[str, float]:
    """Returns (letter_grade, gpa_points) for a given score."""
    if total_marks <= 0:
        return "N/A", 0.0

    percentage = (marks_obtained / total_marks) * 100
    for min_percentage, letter, gpa_points in GRADE_BANDS:
        if percentage >= min_percentage:
            return letter, gpa_points
    return "F", 0.0
