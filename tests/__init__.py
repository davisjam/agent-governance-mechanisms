"""Test-kind modules for the governance-catalogue + skill suite.

The driver (`catalog_tests.py`, run via `python3 catalog.py test`) registers and runs the checks; each
module here owns one *kind* of check (markdown / html / skill / external), sharing helpers via
`tests.common`. Add a new kind = a new module + one line in the driver's CHECKS registry.
"""
