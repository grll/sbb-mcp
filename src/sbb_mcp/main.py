import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from sbb_mcp import gql_queries

mcp = FastMCP("SBB MCP server")


SBB_GRAPHQL_ENDPOINT = "https://graphql.www.sbb.ch/"


@mcp.tool()
def get_places(
    name: str = Field(
        description="The name of the place to search for can be a city or a station name (e.g. 'Zürich', 'Bern', 'Lausanne')"
    ),
) -> dict:
    """get places information by name."""
    headers = {"Content-Type": "application/json"}

    variables = {"input": {"type": "NAME", "value": name}, "language": "EN"}
    payload = {
        "operationName": "GetPlaces",
        "variables": variables,
        "query": gql_queries.get_places,
    }
    try:
        response = httpx.post(
            SBB_GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_trips(
    origin_id: str = Field(
        description="The origin place id (e.g. '8503000' for Zurich HB. can be found by calling get_places)"
    ),
    destination_id: str = Field(
        description="The destination place id (e.g. '8507000' for Bern can be found by calling get_places)"
    ),
    departure_date: str = Field(description="The date of the trip (e.g. '2025-05-01')"),
    departure_time: str = Field(
        description="The time of the trip (e.g. '12:00')", default="12:00"
    ),
) -> dict:
    """get all available trips between two places after a given departure date and time."""
    headers = {"Content-Type": "application/json"}
    input_dict = {
        "places": [
            {"type": "ID", "value": origin_id},
            {"type": "ID", "value": destination_id},
        ],
        "time": {"date": departure_date, "time": departure_time, "type": "DEPARTURE"},
        "includeEconomic": False,
        "directConnection": False,
        "includeAccessibility": "NONE",
        "includeNoticeAttributes": [],
        "includeTransportModes": [
            "HIGH_SPEED_TRAIN",
            "INTERCITY",
            "INTERREGIO",
            "REGIO",
            "URBAN_TRAIN",
            "SPECIAL_TRAIN",
            "SHIP",
            "BUS",
            "TRAMWAY",
            "CABLEWAY_GONDOLA_CHAIRLIFT_FUNICULAR",
        ],
        "includeUnsharp": False,
        "occupancy": "ALL",
        "walkSpeed": 100,
    }
    variables = {"input": input_dict, "pagingCursor": None, "language": "EN"}
    payload = {
        "operationName": "getTrips",
        "variables": variables,
        "query": gql_queries.get_trips,
    }

    try:
        response = httpx.post(
            SBB_GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}


class Trip(BaseModel):
    origin: str = Field(
        description="The origin place id (e.g. '8503000' for Zurich HB. can be found by calling get_places)"
    )
    destination: str = Field(
        description="The destination place id (e.g. '8507000' for Bern can be found by calling get_places)"
    )
    trip_id: str = Field(
        description="The trip id (e.g. '3HA...' can be found by calling get_trips)"
    )


@mcp.tool()
def get_trips_prices(trips: list[Trip]) -> dict:
    """get all available trip prices for a list of trips."""
    headers = {"Content-Type": "application/json"}
    # Build the trips list for the payload
    trips_payload = [
        {"id": trip.trip_id, "fromPlace": trip.origin, "toPlace": trip.destination}
        for trip in trips
    ]
    input_dict = {
        "travelClass": "ANY_CLASS",
        "trips": trips_payload,
        "processId": "4cbeeb86-3847-44f9-95ac-bf19fdadd562",
        "passengers": [{"reductions": ["HALF_FARE"]}],
    }
    variables = {"input": input_dict}
    payload = {
        "query": gql_queries.get_trips_prices,
        "variables": variables,
    }
    try:
        response = httpx.post(
            SBB_GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def buy_ticket(origin: str, destination: str) -> float:
    """Buy a ticket between two places"""
    return f"Ticket bought from {origin} to {destination}"


mcp.run()
