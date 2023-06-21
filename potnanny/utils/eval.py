import re

def evaluate(equation: str) -> bool:
    """
    evaluate a conditional equation str, like:
    ("22 >= 80")        # False
    ("11.1 == 13.9")    # False
    ("2 eq 2.0")        # True

    args:
        - a string statement, like "22 lt 100"
    returns:
        bool (True|False)
    """

    atoms = re.split(r'\s+', equation)
    if len(atoms) != 3:
        raise ValueError("Poorly formed equation '%s'" % equation)

    a = float(atoms[0])
    b = float(atoms[2])
    oper = atoms[1]

    if oper in ['lt','<'] and a < b:
        return True
    elif oper in ['le','<='] and a <= b:
        return True
    elif oper in ['gt','>'] and a > b:
        return True
    elif oper in ['ge','>='] and a >= b:
        return True
    elif oper in ['eq','==', '='] and a == b:
        return True
    elif oper in ['ne','!='] and a != b:
        return True

    return False
