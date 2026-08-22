import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "aft_standards.json"
)


def get_age_group(age):
    if 17 <= age <= 21:
        return "17-21"
    elif 22 <= age <= 26:
        return "22-26"
    elif 27 <= age <= 31:
        return "27-31"
    elif 32 <= age <= 36:
        return "32-36"
    elif 37 <= age <= 41:
        return "37-41"
    elif 42 <= age <= 46:
        return "42-46"
    elif 47 <= age <= 51:
        return "47-51"
    elif 52 <= age <= 56:
        return "52-56"
    elif 57 <= age <= 61:
        return "57-61"
    elif age >= 62:
        return "62+"

    raise ValueError("AFT scoring requires age 17 or older.")


def load_standards():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def time_to_seconds(value):
    """
    Convert a time such as '2:40' into seconds.
    """

    minutes, seconds = value.split(":")

    return int(minutes) * 60 + int(seconds)


def calculate_event_score(
    age,
    gender,
    event,
    performance,
    standard_type="general",
):
    standards = load_standards()

    age_group = get_age_group(age)

    if standard_type == "general":
        event_table = (
            standards["general"]
            [gender.lower()]
            [age_group]
            [event]
        )

    elif standard_type == "combat":
        event_table = (
            standards["combat"]
            [age_group]
            [event]
        )

    else:
        raise ValueError(
            "standard_type must be 'general' or 'combat'"
        )

    # MDL and HRP:
    # Higher number = better performance
    if event in {"mdl", "hrp"}:

        performance = int(performance)

        for points, required in sorted(
            event_table.items(),
            key=lambda item: int(item[0]),
            reverse=True,
        ):
            if performance >= int(required):
                return int(points)

        return 0

    # Plank:
    # Longer time = better performance
    if event == "plank":

        performance_seconds = time_to_seconds(performance)

        for points, required in sorted(
            event_table.items(),
            key=lambda item: int(item[0]),
            reverse=True,
        ):
            required_seconds = time_to_seconds(required)

            if performance_seconds >= required_seconds:
                return int(points)

        return 0

    # SDC and 2-mile run:
    # Lower time = better performance
    if event in {"sdc", "two_mile_run"}:

        performance_seconds = time_to_seconds(performance)

        for points, required in sorted(
            event_table.items(),
            key=lambda item: int(item[0]),
            reverse=True,
        ):
            required_seconds = time_to_seconds(required)

            if performance_seconds <= required_seconds:
                return int(points)

        return 0

    raise ValueError(f"Unknown AFT event: {event}")