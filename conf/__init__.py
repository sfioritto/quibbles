import os

HOME = os.path.join(os.path.expanduser("~"), "quibbles")
EMAIL = os.path.join(HOME, "email")


def home(path="/"):
    return os.path.join(HOME, path)

def email(path="/"):
    return os.path.join(EMAIL, path)


