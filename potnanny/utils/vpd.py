"""
Functions for calculating Vapor Pressure Deficit (VPD)
Formulats derived from here:
    - http://eebweb.arizona.edu/faculty/saleska/SWES.410.510/LECTURES/Dominguez_Microphysics.pdf
"""

def calculate_vpd(t: float, h: float) -> float:
    """
    Calculate the Vapour Pressure Deficit from temp and %rh

    args:
        - Temperature (Celsius)
        - RH(%)
    returns:
        - Float (kPascals)
    """

    svp = calculate_svp(t)
    pa = svp * ((100 - h)/100)
    kpa = pa/1000
    return float("%0.2f" % kpa)


def calculate_svp(t: float) -> float:
    """
    Calculate Saturated Vapour Pressure from temperature

    args:
        - temperature (celsius)
    returns:
        - float (value in Pascals)
    """

    e = 2.7182818284590452353602875
    svp = 611 * e**(t/(t + 237.3) * 17.27)
    return svp

