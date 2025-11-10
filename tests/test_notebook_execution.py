"""
Test that the student's assignment notebook executes without errors.

This test runs the entire notebook and verifies:
- No syntax errors
- No runtime errors  
- All code cells execute successfully
- Required variables and outputs are created
"""

import pytest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path
import tempfile
import shutil


def test_notebook_executes_without_errors():
    """Test that the assignment notebook runs completely without errors."""
    notebook_path = Path("src/assignment.ipynb")
    assert notebook_path.exists(), "Assignment notebook not found"
    
    # Load the notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    # Create a temporary directory for execution
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create proper directory structure: temp_dir/src/ and temp_dir/data/
        src_dir = temp_path / "src"
        src_dir.mkdir()
        
        # Copy notebook to src subdirectory (where it expects to be)
        temp_notebook = src_dir / "assignment.ipynb"
        with open(temp_notebook, 'w') as f:
            nbformat.write(nb, f)
        
        # Copy required data files to temp_dir/data/ (so ../data/ from src/ works)
        data_src = Path("data")
        if data_src.exists():
            data_dst = temp_path / "data" 
            shutil.copytree(data_src, data_dst)
        
        # Create figures directory at temp_dir/figures/ (so ../figures/ from src/ works)
        figures_dir = temp_path / "figures"
        figures_dir.mkdir(exist_ok=True)
        
        # Execute the notebook from the src directory
        ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
        
        try:
            ep.preprocess(nb, {'metadata': {'path': str(src_dir)}})
            print("✓ Notebook executed successfully")
        except Exception as e:
            pytest.fail(f"Notebook execution failed: {str(e)}")


def test_notebook_creates_required_variables():
    """Test that the notebook creates the required variables and functions."""
    notebook_path = Path("src/assignment.ipynb")
    if not notebook_path.exists():
        pytest.skip("Assignment notebook not found")
    
    # Load and execute notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create proper directory structure: temp_dir/src/ and temp_dir/data/
        src_dir = temp_path / "src"
        src_dir.mkdir()
        
        # Setup temporary environment
        temp_notebook = src_dir / "assignment.ipynb"
        with open(temp_notebook, 'w') as f:
            nbformat.write(nb, f)
        
        # Copy data files
        data_src = Path("data")
        if data_src.exists():
            shutil.copytree(data_src, temp_path / "data")
        
        (temp_path / "figures").mkdir(exist_ok=True)
        
        # Execute and capture namespace
        ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
        
        try:
            ep.preprocess(nb, {'metadata': {'path': str(src_dir)}})
            
            # Check that key variables were created by examining the executed cells
            executed_code = []
            for cell in nb.cells:
                if cell.cell_type == 'code' and cell.execution_count is not None:
                    executed_code.append(cell.source)
            
            all_code = '\n'.join(executed_code)
            
            # Verify key elements are present
            assert 'figdir' in all_code, "figdir variable should be defined"
            assert 'ctd_ds' in all_code, "ctd_ds dataset should be loaded"
            assert 'SA_from_SP' in all_code or 'absolute_salinity' in all_code, "TEOS-10 calculations should be performed"
            
            print("✓ Required variables and calculations found")
            
        except Exception as e:
            pytest.fail(f"Failed to verify notebook variables: {str(e)}")


def test_notebook_removes_notimplementederror():
    """Test that student removed all NotImplementedError statements."""
    notebook_path = Path("src/assignment.ipynb")
    if not notebook_path.exists():
        pytest.skip("Assignment notebook not found")
    
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    # Check that no code cells contain NotImplementedError
    remaining_errors = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'code' and 'NotImplementedError' in cell.source:
            remaining_errors.append(f"Cell {i+1}")
    
    assert len(remaining_errors) == 0, f"NotImplementedError still present in cells: {', '.join(remaining_errors)}"
    print("✓ All NotImplementedError statements removed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])