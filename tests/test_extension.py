import unittest
import pandas as pd
import knime.extension as knext
import knime.extension.testing as ktest
import knime.types.chemistry as ktchem
from rdkit import Chem

from src.extension import RDKitObject


class TestRDKitObject(unittest.TestCase):
    """Tests for the RDKitObject node that appends an RDKitMol column."""

    @classmethod
    def setUpClass(cls) -> None:
        # The test plugin and mock chemistry types are registered in tests/conftest.py
        pass

    def test_execute_adds_rdkitmol_from_smiles(self):
        # Given a DataFrame with a KNIME Smiles column (mock type)
        smiles = list(map(ktchem.SmilesValue, ["CC", "O", "c1ccccc1", "CCO"]))
        input_df = pd.DataFrame({"Smiles": smiles})

        node = RDKitObject()
        # Select the molecule column as required by the node
        node.molecule_column = "Smiles"

        input_table = knext.Table.from_pandas(input_df)
        exec_context = ktest.TestingExecutionContext()

        output_table = node.execute(exec_context, input_table)
        output_df = output_table.to_pandas()

        # It should contain the original Smiles and the new RDKitMol column
        self.assertIn("Smiles", output_df.columns)
        self.assertIn("RDKitMol", output_df.columns)
        # RDKitMol should contain RDKit Mol objects or None, and have same length
        self.assertEqual(len(output_df), len(input_df))
        self.assertTrue(all(m is None or isinstance(m, Chem.Mol) for m in output_df["RDKitMol"]))


if __name__ == "__main__":
    unittest.main()
