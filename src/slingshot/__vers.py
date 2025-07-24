import importlib.metadata

try:
    __version__ = importlib.metadata.version("c1s-slingshot-sdk-py")
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"
