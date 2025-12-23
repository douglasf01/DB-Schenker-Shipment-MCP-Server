# DB Schenker Shipment MCP Server
A project for gathering and displaying information about DB Schenker shipments using the public DB Schenker website.

**Note:** This guide is specifically for Linux/Unix systems.


## Description
This project provides a server and a tool for gathering and displaying information about DB Schenker shipments. The MCP (Model Context Protocol) server enables easy connectivity to AI applications and external systems. Additionally, the project includes a tool that cleans and displays this data in a user-friendly format, which is easily parsable by an LLM.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)


## Features
- Automatically starts the MCP server and opens the tool in your web browser.
- Provides a tool for cleaning and displaying shipment data from DB Schenker.
- Displays shipment details in a user and LLM-friendly markdown table.

---

## Prerequisites
Before you begin, ensure you have met the following requirements:

- **Python** >= 3.13
- **Node.js** ^22.7.5 (within major version 22.x.x)
- **uv** package manager >= 0.9.18

### Installing uv
You can install `uv` using `curl`:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installing Node.js
Node.js is best managed using `nvm` (Node Version Manager). Install `nvm` with:
```sh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

Initializes NVM in your current shell session:
```sh
\. "$HOME/.nvm/nvm.sh"
```

Install the latest version of Node.js (v22.x.x):
```sh
nvm install 22
```

Verify the installation by checking the Node.js and npm versions:
```sh
node -v  # Should display "v22.X.X"
npm -v   # Should display the corresponding npm version
```
For more information, you can visist [Node.js](https://nodejs.org/en/download)




## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Grant execute permission to the script:
   ```sh
   chmod +x run.sh
   ```

3. Run the script to set up and start the server:
   ```sh
    ./run.sh
   ```
     This script will:
     - Create a Python virtual environment (if it doesn’t already exist).
     - Activate the virtual environment.
     - Install all necessary dependencies using `uv sync`.
     - Install Playwright (if not already installed).
     - Start the MCP server and open the tool in your default web browser.

  **Note:** The script can be reused to launch the tool.

## Usage
1. After running the script, the tool will automatically open in your web browser at `http://localhost:6274`.
2. Ensure the following alternatives are selected:
   - **Transport Type:** STDIO
   - **Command:** fastmcp
   - **Arguments:** run server.py
3. Press **"Connect"** and wait for the connection to the local MCP server to be established.
4. Press the **"Tools"** button.
5. Press **"List Tools"** to reveal the function **"soup_cleaning"**.
6. Enter a tracking number for a Schenker parcel in the box below **"trackingNum"**.
   - A tracking number is a **10-digit number starting with "180"**.
7. Press **"Run Tool"**. The result should display as **"Success"**, and a markdown table with package information will appear below.
