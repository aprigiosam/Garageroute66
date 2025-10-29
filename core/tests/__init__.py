"""
Utilitário para garantir que `manage.py test` descubra automaticamente todos
os módulos de teste dentro de `core/tests`.
"""

from pathlib import Path
import unittest


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str) -> unittest.TestSuite:
    start_dir = Path(__file__).resolve().parent
    discovered = loader.discover(start_dir=start_dir, pattern=pattern or "test*.py")
    tests.addTests(discovered)
    return tests


__all__ = ["load_tests"]
