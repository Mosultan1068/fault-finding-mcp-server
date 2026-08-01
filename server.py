"""
Fault Finding MCP Server — Proof of Concept

A minimal MCP server that exposes one tool: given a fault category,
it returns the average resolution time for callouts in that category,
based on data/callouts.csv.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP
import pandas as pd

# Create the MCP server instance. This name is what shows up
# when an MCP client (e.g. Claude Desktop) lists available servers.
mcp = FastMCP("fault-finding-server")

# Build the CSV path relative to THIS FILE's location, not relative to
# whatever folder the process happens to be launched from. This matters
# because Claude Desktop launches the server from its own working
# directory, not from C:\fault_finding\ — so a plain relative path like
# "data/callouts.csv" would fail with FileNotFoundError.
CSV_PATH = Path(__file__).resolve().parent / "data" / "callouts.csv"

# Load the CSV once at startup, into memory, as a pandas DataFrame.
# For a proof of concept this is fine; a production version would
# handle reloads, larger data, and error handling more carefully.
df = pd.read_csv(CSV_PATH)


@mcp.tool()
def get_average_resolution_time(fault_category: str) -> str:
    """
    Get the average resolution time (in minutes) for a given fault category.

    Args:
        fault_category: The type of fault to look up, e.g. "Battery",
            "Engine", "Tyre Puncture", "Fuel Issue", "Electrical",
            "Overheating", "Lockout", "Brake Failure".

    Returns:
        A short message with the average resolution time and how many
        callouts it was based on, or a message saying no data was found.
    """
    # Filter the DataFrame for rows matching the requested category.
    # case=False makes the match case-insensitive so "battery" and
    # "Battery" both work.
    matches = df[df["fault_category"].str.lower() == fault_category.lower()]

    if matches.empty:
        return f"No callouts found for fault category '{fault_category}'."

    average_time = matches["resolution_time_mins"].mean()
    count = len(matches)

    return (
        f"Average resolution time for '{fault_category}' faults: "
        f"{average_time:.1f} minutes (based on {count} callouts)."
    )


# This starts the server and makes it listen for requests from an MCP client.
# Using stdio transport, which is the simplest option and works directly
# with Claude Desktop and other local MCP clients.
if __name__ == "__main__":
    mcp.run(transport="stdio")