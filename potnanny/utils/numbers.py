def is_number(val):
    """
    check if a string can be cast to an int or float successfully.
    args:
        - str ("13.0", "42")
    returns:
        - type of number it matches (int, float) or None
    """

    if type(val) is str and val.isdigit():
        return int

    try:
        f = float(val)
        return float
    except:
        pass

    return None
