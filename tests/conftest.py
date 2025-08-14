import os
import sys
import importlib
from types import ModuleType

# Ensure repository root is on sys.path so `import src` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure the mock chemistry package is importable
TEST_DIR = os.path.dirname(__file__)
MOCK_PY_SRC = os.path.join(TEST_DIR, "test", "python", "src")
if MOCK_PY_SRC not in sys.path:
    sys.path.insert(0, MOCK_PY_SRC)

# Register the test plugin (adds python/src to path for KNIME plugin resolution)
try:
    import knime.extension.testing as ktest
    PLUGIN_XML = os.path.join(TEST_DIR, "test", "plugin.xml")
    if os.path.isfile(PLUGIN_XML):
        ktest.register_extension(PLUGIN_XML)
except Exception:
    # Keep tests importable even if KNIME test utilities are unavailable
    pass

# Alias org.knime.types.chemistry -> knime.types.chemistry so project code can `from knime.types.chemistry import ...`
try:
    import knime  # ensure parent package exists
    org_chem = importlib.import_module("org.knime.types.chemistry")

    # Ensure knime.types is present as a package-like module
    if "knime.types" not in sys.modules:
        types_pkg = ModuleType("knime.types")
        # Mark it as a package-ish module so submodules can be attached
        types_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["knime.types"] = types_pkg
        # attach as attribute on knime package
        setattr(knime, "types", types_pkg)

    # Map chemistry submodule
    sys.modules["knime.types.chemistry"] = org_chem
    # Attach attribute on knime.types for attribute-style access
    setattr(sys.modules["knime.types"], "chemistry", org_chem)
except Exception:
    # If the mock isn't present, leave imports unchanged
    pass
