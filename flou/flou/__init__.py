try:
    from importlib.metadata import version
    __version__ = version("flou")
except ImportError:
    from importlib_metadata import version  # type: ignore
    __version__ = version("flou")
except Exception:
    __version__ = "unknown"
