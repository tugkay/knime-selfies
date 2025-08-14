import os
import sys

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
