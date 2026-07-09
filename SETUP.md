# RAHUUL_RADAR Setup Guide

Welcome to the **RAHUUL_RADAR** project. This guide will walk you through setting up a clean, isolated environment to run the application on a fresh machine (macOS, Linux, or Windows).

## Prerequisites

- **Python 3.12+** installed on your system.

## Setup Instructions

**1. Create a Virtual Environment**
It's highly recommended to use a virtual environment to keep dependencies isolated.

```bash
# Navigate to the project directory
cd /path/to/RAHUUL_RADAR

# Create the virtual environment
python3 -m venv .venv
```

**2. Activate the Virtual Environment**

On macOS and Linux:
```bash
source .venv/bin/activate
```

On Windows:
```cmd
.venv\Scripts\activate
```

**3. Install Dependencies**
Install all required libraries for running and testing the app.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Compile the Project (Optional but recommended)**
Pre-compile the Python files to ensure there are no glaring syntax errors across the project.
```bash
python -m compileall .
```

## Running the Application

Once dependencies are installed, you can launch the desktop scanner:

```bash
python main.py
```

## Running the Tests

To verify that the environment is fully operational, run the automated test suite. Since this is a GUI application, we recommend running tests in an offscreen mode if you're executing them in a CI/CD or headless environment.

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q
```
