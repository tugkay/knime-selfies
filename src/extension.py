import logging
import knime.extension as knext
from knime.types.chemistry import to_rdkit_series, is_molecule
from knime.types.chemistry import SmilesValue
from rdkit import Chem
import selfies as sf
import pandas as pd

LOGGER = logging.getLogger(__name__)   
    
# @knext.node(name="RDKitMol from any Mol Type", node_type=knext.NodeType.MANIPULATOR, icon_path="icon.png", category="/")
# @knext.input_table(name="Input Data", description="Input table containing any mol type")
# @knext.output_table(name="Output Data", description="Input table appended with a column containing RDKit molecule")
# class RDKitObject:
#     """
#     This node returns the RDKit molecule in an appended column.
#     """
#     # Note: is_molecule is used to filter columns that contain any usable molecule type.
#     molecule_column = knext.ColumnParameter(label="Select the column containing any mol type", description="Choose the column from the input table containing the mol type", column_filter=is_molecule)

#     def configure(self, configure_context, input_schema_1):
#         return input_schema_1.append(knext.Column(knext.logical(Chem.Mol), "RDKitMol")) # RDKitMol is a type that is known to KNIME and can be used in the output table.
 
 
#     def execute(self, exec_context, input_1):    
#         input_1_pandas = input_1.to_pandas()
#         #input_1_pandas['RDKitMol'] = input_1_pandas[self.molecule_column].astype("Molecule")  # This is unfortunately not yet supported in KNIME python extensions (2025-07-23)
#         input_1_pandas['RDKitMol'] = to_rdkit_series(input_1_pandas[self.molecule_column]) # Note: We can convert any molecule type to RDKitMol using this function. And simply add the new column to the DataFrame.
#         return knext.Table.from_pandas(input_1_pandas)
    

# @knext.node(name="Count Num Carbons", node_type=knext.NodeType.MANIPULATOR, icon_path="icon.png", category="/")
# @knext.input_table(name="Input Data", description="Input table containing RDKit molecules")
# @knext.output_table(name="Output Data", description="Input table with a column containing the number of carbons")
# class CountNumCarbons:
#     """
#     This node counts the number of carbons in each RDKit molecule and appends it as a new column.

#     The provided KNIME workflow demonstrates how to use this node:
#         - directly from a SMILES column
#         - from a column containing Java RDKit molecules
#         - from another python node that outputs RDKit molecules
#     """
#     molecule_column = knext.ColumnParameter(label="Select the column containing RDKit molecules", description="Choose the column from the input table containing RDKit molecules", column_filter=is_molecule)
    
#     def configure(self, configure_context, input_schema_1):
#         LOGGER.warning(f"DEBUG: Input schema : {dir(input_schema_1)}")
#         for col in input_schema_1._columns:
#             LOGGER.warning(f"Column: {col.name}, Type: {col.ktype}")   # Debugging line to check input types
#         return input_schema_1.append(knext.Column(knext.int64(), "NumCarbons"))


#     def execute(self, exec_context, input_1):
#         df = input_1.to_pandas()
#         mol_col = to_rdkit_series(df[self.molecule_column], sanitize=True)
#         df['NumCarbons'] = mol_col.apply(lambda mol: sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 6))
#         return knext.Table.from_pandas(df)


# @knext.node(name="Chemistry API Introspection", node_type=knext.NodeType.MANIPULATOR, icon_path="icon.png", category="/")
# @knext.input_table(name="Input Data", description="Pass-through table")
# @knext.output_table(name="Output Data", description="Unchanged input; logs chemistry API")
# class ChemistryApiIntrospection:
#     """
#     Run this once to log what's available under knime.types.chemistry in your KNIME AP.
#     Check KNIME Console and knime.log for the output.
#     """

#     def configure(self, configure_context, input_schema):
#         return input_schema

#     def execute(self, exec_context, input_table):
#         chem = __import__("knime.types.chemistry", fromlist=["*"])
#         LOGGER.warning("knime.types.chemistry contents: %s", dir(chem))
#         for name in dir(chem):
#             try:
#                 LOGGER.warning("chem.%s -> %r", name, getattr(chem, name))
#             except Exception as e:
#                 LOGGER.warning("chem.%s -> <error: %s>", name, e)
#         df = input_table.to_pandas()
#         return knext.Table.from_pandas(df)


@knext.node(name="SMILES to SELFIES", node_type=knext.NodeType.MANIPULATOR, icon_path="icon.png", category="/")
@knext.input_table(name="Input Data", description="Input table containing SMILES strings")
@knext.output_table(name="Output Data", description="Input table appended with a SELFIES column")
class SmilesToSelfies:
    """
    Convert SMILES strings into SELFIES and append them as a new column.
    """

    smiles_column = knext.ColumnParameter(
        label="Select the column containing SMILES",
        description="Choose the column that contains SMILES",
        column_filter=lambda col: col.ktype in (knext.string(), knext.logical(SmilesValue))
    )

    output_column_name = knext.StringParameter(
        label="Output column name",
        description="Name of the output column for SELFIES",
        default_value="SELFIES"
    )

    def configure(self, configure_context, input_schema):
        return input_schema.append(knext.Column(knext.string(), str(self.output_column_name)))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        def to_selfies(s):
            if isinstance(s, str) and s:
                try:
                    return sf.encoder(s)
                except Exception:
                    return None
            return None
        out_col = str(self.output_column_name)
        df[out_col] = df[self.smiles_column].apply(to_selfies)
        return knext.Table.from_pandas(df)


@knext.node(name="SELFIES to SMILES", node_type=knext.NodeType.MANIPULATOR, icon_path="icon.png", category="/")
@knext.input_table(name="Input Data", description="Input table containing SELFIES strings")
@knext.output_table(name="Output Data", description="Input table appended with a SMILES column")
class SelfiesToSmiles:
    """
    Convert SELFIES strings into SMILES and append them as a new column.
    """

    selfies_column = knext.ColumnParameter(
        label="Select the column containing SELFIES",
        description="Choose the column that contains SELFIES",
        column_filter=lambda col: col.ktype == knext.string()
    )

    output_column_name = knext.StringParameter(
        label="Output column name",
        description="Name of the output column for SMILES",
        default_value="SMILES"
    )

    def configure(self, configure_context, input_schema):
        return input_schema.append(knext.Column(knext.logical(SmilesValue), str(self.output_column_name)))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        def to_smiles(s):
            if isinstance(s, str) and s:
                try:
                    return sf.decoder(s)
                except Exception:
                    return None
            return None
        out_col = str(self.output_column_name)
        df[out_col] = df[self.selfies_column].apply(to_smiles)
        # Cast to SmilesValue for correct KNIME data type
        df[out_col] = df[out_col].apply(lambda x: SmilesValue(x) if x else None)
        return knext.Table.from_pandas(df)


