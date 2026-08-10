import json
from pathlib import Path

import pdfplumber


PDF_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "raw"
    / "aft_scoring_scales.pdf"
)

OUTPUT_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "aft_standards.json"
)


AGE_GROUPS = [
    "17-21",
    "22-26",
    "27-31",
    "32-36",
    "37-41",
    "42-46",
    "47-51",
    "52-56",
    "57-61",
    "62+",
]


def identify_event(title):
    title = title.lower()

    if "deadlift" in title:
        return "mdl"

    if "push-up" in title:
        return "hrp"

    if "sprint" in title and "drag" in title:
        return "sdc"

    if "plank" in title:
        return "plank"

    if "two-mile" in title or "two mile" in title:
        return "two_mile_run"

    return None


def create_empty_structure():
    data = {
        "general": {
            "male": {},
            "female": {},
        },
        "combat": {},
    }

    for age_group in AGE_GROUPS:
        data["general"]["male"][age_group] = {}
        data["general"]["female"][age_group] = {}
        data["combat"][age_group] = {}

    return data


def parse_pdf():
    standards = create_empty_structure()

    with pdfplumber.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                continue

            table = tables[0]

            if len(table) < 5:
                continue

            # Row 1 contains the event title.
            title = table[1][1] or ""

            event = identify_event(title)

            if event is None:
                print(
                    f"Skipping page {page_number}: "
                    f"could not identify event"
                )
                continue

            print(
                f"Processing page {page_number}: {event}"
            )

            # Initialize event dictionaries.
            for age_group in AGE_GROUPS:

                standards["general"]["male"][
                    age_group
                ].setdefault(event, {})

                standards["general"]["female"][
                    age_group
                ].setdefault(event, {})

                standards["combat"][
                    age_group
                ].setdefault(event, {})

            # Data begins on row 4.
            for row in table[4:]:

                if not row:
                    continue

                points = row[0]

                if not points:
                    continue

                try:
                    int(points)
                except ValueError:
                    continue

                # Each age group occupies two columns:
                #
                # M | C
                # F
                #
                # Columns:
                #
                # 0 = Points
                # 1 = 17-21 M|C
                # 2 = 17-21 F
                # 3 = 22-26 M|C
                # 4 = 22-26 F
                # ...
                # 21 = duplicate Points

                for index, age_group in enumerate(
                    AGE_GROUPS
                ):

                    male_column = 1 + (index * 2)
                    female_column = male_column + 1

                    male_value = row[male_column]
                    female_value = row[female_column]

                    if (
                        male_value
                        and male_value != "---"
                    ):
                        standards[
                            "general"
                        ]["male"][
                            age_group
                        ][event][points] = male_value

                        # Official table combines M | C.
                        standards[
                            "combat"
                        ][age_group][event][
                            points
                        ] = male_value

                    if (
                        female_value
                        and female_value != "---"
                    ):
                        standards[
                            "general"
                        ]["female"][
                            age_group
                        ][event][points] = female_value

    return standards


def main():
    standards = parse_pdf()

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            standards,
            file,
            indent=2,
        )

    print()
    print(
        f"AFT standards written to:"
        f" {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()