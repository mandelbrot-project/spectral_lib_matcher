def logBuilder(verbose: bool):
    if (verbose):
        return lambda string: print(string)
    else:
        return lambda string: None
