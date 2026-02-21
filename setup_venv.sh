#!/bin/bash

# Define environment name
ENV_NAME="ex00"

# Create the environment
echo "Creating venv: $ENV_NAME..."
python3 -m venv $ENV_NAME

# Initialize for the script shell
source $ENV_NAME/bin/activate

# Upgrade pip first
pip install --upgrade pip

# --- Conditional Installation Logic ---
# -s checks if the file exists and has a size greater than zero
if [ -s "requirements.txt" ]; then
    echo "requirements.txt found and not empty. Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt is empty or missing. Installing default packages..."
    pip install numpy pandas tabulate jupyter matplotlib plotly
fi
# ---------------------------------------

# Running jupyter server
echo "Starting jupyter server on port 8891..."
jupyter notebook --port 8891
