"""
Test actual outputs produced by students.
This tests what students actually created, not their code.
"""

import pytest
import xarray as xr
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def test_student_information_completed():
    """Test that student filled in their personal information."""
    notebook_path = Path("src/assignment.ipynb")
    if not notebook_path.exists():
        pytest.skip("Assignment notebook not found")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Find student information cell
    info_cell = None
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source'])
            if ('Your Name:' in source or 'Author:' in source or 
                'Complete your information' in source or 'Your Information' in source):
                info_cell = source
                break
    
    assert info_cell is not None, "Could not find student information cell"
    
    # Check that placeholders have been replaced
    placeholders = [
        '[YOUR NAME HERE]',
        '[TODAY\'S DATE]',
        '[REPLACE WITH YOUR ACTUAL NAME]',
        '[REPLACE WITH TODAY\'S DATE]',
        '[REPLACE WITH YOUR STUDENT ID]',
        'YourName',
        'Your Name Here'
    ]
    
    for placeholder in placeholders:
        assert placeholder not in info_cell, f"Student information incomplete: '{placeholder}' still present"


def test_netcdf_file_created():
    """Test that student successfully converted CNV to netCDF."""
    netcdf_file = Path("data/MSM121_054_1db.nc")
    assert netcdf_file.exists(), "NetCDF file was not created - CNV conversion not completed"


def test_netcdf_file_valid():
    """Test that the netCDF file contains expected oceanographic data."""
    netcdf_file = Path("data/MSM121_054_1db.nc")
    if not netcdf_file.exists():
        pytest.skip("NetCDF file not found")
    
    # Load and check the dataset
    ds = xr.open_dataset(netcdf_file)
    
    # Check required variables exist - use the actual variable names from the data
    required_vars = ['pressure']
    for var in required_vars:
        assert var in ds.data_vars, f"Required variable '{var}' missing from netCDF file"
    
    # Check for salinity variable (could be 'salinity' or another name)
    salinity_vars = ['salinity', 'PSAL', 'sal', 'PSAL_1', 'PSAL1']
    sal_found = any(var in ds.data_vars for var in salinity_vars)
    assert sal_found, f"No salinity variable found. Available variables: {list(ds.data_vars.keys())}"
    
    # Check data is reasonable
    assert len(ds.pressure) > 50, "Dataset should have at least 50 pressure levels"
    # Find salinity variable and check values
    salinity_vars = ['salinity', 'PSAL', 'sal', 'PSAL_1', 'PSAL1']
    sal_var = None
    for var in salinity_vars:
        if var in ds.data_vars:
            sal_var = var
            break
    
    if sal_var:
        assert ds[sal_var].min() > 30, f"Salinity data appears invalid (too low): {ds[sal_var].min()}"
        assert ds[sal_var].max() < 40, f"Salinity data appears invalid (too high): {ds[sal_var].max()}"


def test_teos10_calculations_completed():
    """Test that TEOS-10 variables were actually calculated and added."""
    netcdf_file = Path("data/MSM121_054_1db_edited.nc")
    if not netcdf_file.exists():
        pytest.skip("Edited netCDF file not found")
    
    ds = xr.open_dataset(netcdf_file)
    
    # Check TEOS-10 variables were added
    assert 'absolute_salinity' in ds.data_vars, "Absolute salinity not calculated"
    assert 'conservative_temperature' in ds.data_vars, "Conservative temperature not calculated"
    
    # Check they have reasonable values
    SA = ds.absolute_salinity
    CT = ds.conservative_temperature
    
    assert SA.min() > 30, "Absolute salinity values too low"
    assert SA.max() < 40, "Absolute salinity values too high" 
    assert CT.min() > -2, "Conservative temperature too low"
    assert CT.max() < 30, "Conservative temperature too high"
    
    # Check they're different from practical/in-situ values
    # Find the original salinity and temperature variables
    sal_vars = ['salinity', 'PSAL', 'sal', 'PSAL_1', 'PSAL1']
    temp_vars = ['temperature', 'temperature_1', 'TEMP', 'temp', 'TEMP_1', 'TEMP1']
    
    original_sal = None
    original_temp = None
    
    for var in sal_vars:
        if var in ds.data_vars:
            original_sal = var
            break
            
    for var in temp_vars:
        if var in ds.data_vars:
            original_temp = var
            break
    
    if original_sal:
        assert not np.allclose(SA, ds[original_sal]), "Absolute salinity identical to practical salinity"
    
    if original_temp:
        assert not np.allclose(CT, ds[original_temp]), "Conservative temperature identical to in-situ temperature"


def test_all_figures_created():
    """Test that all 4 required figures were created."""
    figures_dir = Path("figures/")
    if not figures_dir.exists():
        pytest.skip("Figures directory not found")
    
    # Check each required figure exists
    required_figures = [
        'ex1fig1-*-Messfern.png',
        'ex1fig2-*-Messfern.png', 
        'ex1fig3-*-Messfern.png',
        'ex1fig4-*-Messfern.png'
    ]
    
    for pattern in required_figures:
        matching_files = list(figures_dir.glob(pattern))
        assert len(matching_files) > 0, f"Required figure not found: {pattern}"
        
        # Check it's not the template name
        for fig_file in matching_files:
            assert 'YourName' not in fig_file.name, f"Figure name not personalized: {fig_file}"


def test_figures_contain_data():
    """Test that figures actually contain plotted data (not just empty plots)."""
    figures_dir = Path("figures/")
    if not figures_dir.exists():
        pytest.skip("Figures directory not found")
    
    figure_files = list(figures_dir.glob("ex1fig*-*-Messfern.png"))
    if len(figure_files) == 0:
        pytest.skip("No figures found")
    
    # Test the first figure we find
    test_fig = figure_files[0]
    
    # Load image and check it's not just white/empty
    img = mpimg.imread(test_fig)
    
    # Check image has reasonable dimensions
    assert img.shape[0] > 100, "Figure height too small"
    assert img.shape[1] > 100, "Figure width too small"
    
    # Check it's not just a white image (relaxed threshold for profile plots)
    mean_pixel = np.mean(img)
    assert mean_pixel < 0.99, f"Figure appears to be mostly empty/white: {test_fig} (mean pixel: {mean_pixel:.4f})"


def test_figure_file_sizes():
    """Test that figure files have reasonable sizes (not tiny empty files)."""
    figures_dir = Path("figures/")
    if not figures_dir.exists():
        pytest.skip("Figures directory not found")
    
    figure_files = list(figures_dir.glob("ex1fig*-*-Messfern.png"))
    
    for fig_file in figure_files:
        file_size = fig_file.stat().st_size
        assert file_size > 10000, f"Figure file too small (likely empty): {fig_file} ({file_size} bytes)"
        assert file_size < 5000000, f"Figure file too large: {fig_file} ({file_size} bytes)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])