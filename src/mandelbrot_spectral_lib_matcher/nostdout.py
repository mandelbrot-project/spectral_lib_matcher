#!/usr/bin/env python3

import contextlib
import io
import sys


# define a warning silencer that disables stdout temporarily, use it with a with nostdout(): block
# see https://stackoverflow.com/a/2829036

@contextlib.contextmanager
def nostdout(active=True):
    if active:
        save_stdout = sys.stdout
        sys.stdout = io.StringIO()
    yield
    if active:
        sys.stdout = save_stdout
