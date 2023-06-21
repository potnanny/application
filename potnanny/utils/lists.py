def flatten_list(mylist):
    """
    Recursively flatten a list which may contain other lists
    args:
        - list
    returns:
        - a new list
    """

    results = []
    for i in mylist:
        if type(i) is list:
            results += flatten_list(i)
        else:
            results.append(i)

    return results
