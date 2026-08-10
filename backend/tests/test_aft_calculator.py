from src.aft_calculator import get_age_group
from src.aft_calculator import calculate_event_score


def test_age_groups():
    assert get_age_group(20) == "17-21"
    assert get_age_group(25) == "22-26"
    assert get_age_group(30) == "27-31"
    assert get_age_group(35) == "32-36"
    assert get_age_group(37) == "37-41"
    assert get_age_group(45) == "42-46"
    assert get_age_group(50) == "47-51"
    assert get_age_group(55) == "52-56"
    assert get_age_group(60) == "57-61"
    assert get_age_group(65) == "62+"


def test_calculate_plank_score():
    score = calculate_event_score(
        age=37,
        gender="female",
        event="plank",
        performance="2:40",
    )

    assert score == 87

from src.aft_calculator import (
    calculate_event_score,
    get_age_group,
    time_to_seconds,
)


def test_age_groups():
    assert get_age_group(20) == "17-21"
    assert get_age_group(25) == "22-26"
    assert get_age_group(37) == "37-41"
    assert get_age_group(65) == "62+"


def test_time_conversion():
    assert time_to_seconds("2:40") == 160
    assert time_to_seconds("1:10") == 70
    assert time_to_seconds("19:30") == 1170


def test_female_37_41_plank_100():
    score = calculate_event_score(
        age=37,
        gender="female",
        event="plank",
        performance="3:20",
    )

    assert score == 100


def test_female_37_41_plank_60():
    score = calculate_event_score(
        age=37,
        gender="female",
        event="plank",
        performance="1:10",
    )

    assert score == 60


def test_female_37_41_plank_between_thresholds():
    score = calculate_event_score(
        age=37,
        gender="female",
        event="plank",
        performance="2:40",
    )

    assert score == 87