"""Weather risk rules from the assessment.

Units: wind in mph, rain and snow in inches per hour, load in pounds.
Risk levels are numbers so we can compare them: higher number = more dangerous.
"""

LEVEL_NAMES = ["low", "moderate", "high", "severe", "no_travel"]

LOW = 0
MODERATE = 1
HIGH = 2
SEVERE = 3
NO_TRAVEL = 4


def wind_level(mph):
    if mph < 25:
        return LOW
    if mph < 35:
        return MODERATE
    if mph < 45:
        return HIGH
    if mph < 55:
        return SEVERE
    return NO_TRAVEL  # 55 mph or more


def rain_level(inches):
    if inches < 0.10:
        return LOW
    if inches < 0.25:
        return MODERATE
    if inches < 0.50:
        return HIGH
    if inches <= 1.00:
        return SEVERE
    return NO_TRAVEL  # more than 1.00


def snow_level(inches):
    if inches < 0.5:
        return LOW
    if inches < 1.0:
        return MODERATE
    if inches < 2.0:
        return HIGH
    if inches <= 3.0:
        return SEVERE
    return NO_TRAVEL  # more than 3.0


def get_risk(wind, rain, snow, load):
    """Return the risk level (0-4) for one checkpoint."""
    # Step 1: the worst of the three weather conditions.
    level = max(wind_level(wind), rain_level(rain), snow_level(snow))

    # Step 2: heavy loads make wind more dangerous (this can only raise the level).
    if wind >= 45 and load > 30000:
        level = NO_TRAVEL
    elif wind >= 35 and wind < 45 and load > 40000:
        level = max(level, SEVERE)

    return level
