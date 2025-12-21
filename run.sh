#!/bin/bash

#Check if the virtual environment directory exists
if [ -d ".venv" ]; then
    echo "Virtual environment exists."
else
    echo "Creating virtual environment..."
    uv venv
fi

#Activate the virtual environment
source .venv/bin/activate

#Sync dependencies
uv sync

#Check if Playwright has been installed
if [ ! -f ".playwright_installed" ]; then
    echo "Installing Playwright..."
    playwright install
    #Create a flag file to indicate that Playwright is installed
    touch .playwright_installed
else
    echo "Playwright is already installed."
fi
#Run the server
<<<<<<< HEAD
npx @modelcontextprotocol/inspector fastmcp run server.py
=======
npx @modelcontextprotocol/inspector fastmcp run server.py
>>>>>>> 9a995b142b3527f8456b0b047df9c9d11c5c4f42
