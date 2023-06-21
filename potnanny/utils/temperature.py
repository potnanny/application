def convert_to_fahrenheit(celsius):
    """
    Convert a celsius temperature to fahrenheit.
    args:
        - a celsius number
    returns:
        - a fahrenheit number (float)
    """

    result = None
    try:
        result = (celsius * 1.8) + 32
    except:
        pass

    return result
