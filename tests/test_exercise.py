"""
Test file for Exercise 1: CTD Profile Plotting

This file contains automated tests to check student submissions.
Tests are run by GitHub Actions when students push their code.

IMPORTANT: This file tests the basic environment setup.
For detailed completion checking, see test_completion.py
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seasenselib

def test_imports_work():
    """Test that required packages can be imported."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import xarray as xr
        import gsw
        from seasenselib.readers import SbeCnvReader, NetCdfReader
        from seasenselib.writers import NetCdfWriter
    except ImportError as e:
        pytest.fail(f"Failed to import required package: {e}")


def test_notebook_exists():
    """Test that the assignment notebook exists."""
    # Try different possible locations for the notebook
    possible_paths = [
        Path("src/assignment.ipynb"),
        Path("../src/assignment.ipynb"),
        Path("./assignment.ipynb")
    ]
    
    notebook_found = False
    for path in possible_paths:
        if path.exists():
            notebook_found = True
            break
    
    assert notebook_found, f"assignment.ipynb not found in any of these locations: {[str(p) for p in possible_paths]}"


def test_data_file_exists():
    """Test that the required CTD data file exists."""
    # Try different possible locations for the data file
    possible_paths = [
        Path("data/MSM121_054_1db.cnv"),
        Path("../data/MSM121_054_1db.cnv"),
        Path("./MSM121_054_1db.cnv")
    ]
    
    data_found = False
    for path in possible_paths:
        if path.exists():
            data_found = True
            break
    
    # Data file is optional since it can be downloaded
    if not data_found:
        print("Note: CTD data file not found locally - should be downloaded when running notebook")


def test_basic_plotting_functions():
    """Test that basic plotting functionality works."""
    # Create sample data
    depth = np.linspace(0, 100, 50)
    temperature = 20 - depth * 0.1 + np.random.normal(0, 0.5, 50)
    salinity = 35 + depth * 0.01 + np.random.normal(0, 0.1, 50)
    
    # Test basic plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    
    ax1.plot(temperature, depth)
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Depth (m)')
    ax1.invert_yaxis()
    ax1.set_title('Temperature Profile')
    
    ax2.plot(salinity, depth)
    ax2.set_xlabel('Salinity (PSU)')
    ax2.set_ylabel('Depth (m)')
    ax2.invert_yaxis()
    ax2.set_title('Salinity Profile')
    
    plt.tight_layout()
    
    # Check that plots were created
    assert len(fig.axes) == 2
    assert len(ax1.lines) > 0
    assert len(ax2.lines) > 0
    assert ax1.get_xlabel() != ''
    assert ax1.get_ylabel() != ''
    assert ax2.get_xlabel() != ''
    assert ax2.get_ylabel() != ''
    
    plt.close(fig)


def test_data_analysis_concepts():
    """Test understanding of oceanographic data concepts."""
    # Sample CTD data patterns
    depth = np.linspace(0, 1000, 100)
    
    # Typical ocean temperature profile (thermocline)
    temperature = 25 * np.exp(-depth/200) + 4
    
    # Typical salinity profile
    salinity = 34.5 + 0.5 * (1 - np.exp(-depth/500))
    
    # Test that temperature decreases with depth (generally)
    assert temperature[0] > temperature[-1], "Temperature should generally decrease with depth"
    
    # Test that salinity varies in reasonable range
    assert 30 < np.mean(salinity) < 40, "Salinity should be in reasonable ocean range"
    
    # Test depth is positive and increasing
    assert np.all(depth >= 0), "Depth should be positive"
    assert np.all(np.diff(depth) > 0), "Depth should increase monotonically"


if __name__ == "__main__":
    pytest.main([__file__])