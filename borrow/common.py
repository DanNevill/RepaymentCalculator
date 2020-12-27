#!/usr/bin/env python3
from typing import Tuple, TypeVar


Numeric = TypeVar('Numeric', int, float)
NumStr  = TypeVar('NumStr',  str, Numeric)

def sanitize_percent(value: NumStr) -> Numeric:

    """Determines percentage in decimal form
    for string inputs.

    Arguments:
      - value (Numeric/str): percentage in
      string or decimal form.

    Return:
      - float: if string depicts percentage.
      - Numeric: if Numeric provided."""

    # Strip whitespace from strings
    #
    if (type(value) is str):
        value = value.strip()

    # If value endswith a percent
    # symbol then transform to 
    # percentage decimal
    #
    if value[-1] == '%':
        value = float(value[:-1]) / 100

    return value


def sign_magnitude(value: NumStr) -> Tuple[Numeric, Numeric]:

    """Determines both sign and magnitude of a
    string or Numeric input.

    Arguments:
      - value (Numeric/str): value to extract
        numeric sign and magnitude from.

    Return:
      - Tuple:
        - Numeric: sign (+/-) of input.
        - Numeric: absolute value of input."""

    # Default values:
    # +<value>
    #
    sign = 1.0 
    value = value

    # If numeric return sign multiplier
    # and absolute value for magnitude
    #
    if (type(value) in [float, int]):
        if (value < 0):
            sign = -1.0
        value = abs(value)

    # If string check first character
    # for sign and strip it for magnitude
    #
    else:
        if (value[0] in ['+', '-']):
            if (value[0] == '-'):
                sign = -1.0
            value = value[1:]

    return (sign, value)


def signed_float_to_string(sign: Numeric, magnitude: Numeric) -> Tuple[str, str]:

    """Translates sign and magnitude tuple
    into string form from numeric.

    Arguments:
      - sign (Numeric): sign (+/-) or input.
      - magnitude (Numeric): absolute value
      of input.

    Return:
      - Tuple:
        - str: sign character (+/-) of input.
        - str: textual value to 2 decimal
        places."""

    # Format currency to 2 d.p.
    # and extract associated sign
    #
    magnitude = "{0:.2f}".format(magnitude)
    sign      = "-" if sign < 0 else " "

    return (sign, magnitude)

