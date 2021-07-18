"""
Manage our internal binary format for databases.
"""

import pickle


def write_binary_database(database, file):
    file.write(b"MANDELBROTDBV0.1\n")
    pickle.dump(database, file)


def read_binary_database(file):
    # We search for the header of our special format
    # we do that because somehow pickle can read some of our MGF files as a pickle file…
    first_line = file.readline()
    if first_line.startswith(b"MANDELBROTDBV"):
        return pickle.load(file)
    else:
        return None
