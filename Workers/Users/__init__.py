import os

userFolders = os.listdir(os.path.dirname(__file__))

__all__ = []

for basename in userFolders:
    if "__" not in basename:
        __all__ += [basename]
