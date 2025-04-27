import asyncio
from typing import Literal
import httpx
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from sbb_mcp import gql_queries
from sbb_mcp.models import StopPlace, Trip

mcp = FastMCP("SBB MCP server")


SBB_GRAPHQL_ENDPOINT = "https://graphql.www.sbb.ch/"


async def get_places(
    client: httpx.AsyncClient,
    name: str = Field(
        description="The name of the place to search for can be a city or a station name or an address (e.g. 'Zürich HB', 'Bern', 'Lausanne', 'Rue de la gare 1, 1000 Lausanne')"
    ),
) -> list[StopPlace] | dict[Literal["error"], str]:
    """get places information by name."""
    variables = {"input": {"type": "NAME", "value": name}, "language": "EN"}
    payload = {
        "operationName": "GetPlaces",
        "variables": variables,
        "query": gql_queries.get_places,
    }
    try:
        response = await client.post(SBB_GRAPHQL_ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        stop_places = [
            StopPlace(**place) for place in data.get("data", {}).get("places", [])
        ]
        return stop_places
    except Exception as e:
        return {"error": str(e)}


async def _get_trips(
    client: httpx.AsyncClient,
    origin_id: str,
    destination_id: str,
    departure_date: str,
    departure_time: str,
) -> list[Trip] | dict[Literal["error"], str]:
    """get all available trips between two places after a given departure date and time."""
    input_dict = {
        "places": [
            {"type": "ID", "value": origin_id},
            {"type": "ID", "value": destination_id},
        ],
        "time": {
            "date": departure_date,
            "time": departure_time,
            "type": "DEPARTURE",
        },
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
        response = await client.post(SBB_GRAPHQL_ENDPOINT, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        breakpoint()
        return [
            Trip(**trip)
            for trip in data.get("data", {}).get("trips", {}).get("trips", [])
        ]
    except Exception as e:
        return {"error": str(e)}


# async def get_trip_prices(
#     client: httpx.AsyncClient,
#     trip_id: str,
# ) -> list[TripPrice] | dict[Literal["error"], str]:
#     """get all available trip prices for a given trip id."""
#     pass


@mcp.tool()
async def get_trips(
    ctx: Context,
    origin_name: str = Field(
        description="The name of the place of origin to search for can be a city or a station name or an address (e.g. 'Zürich HB', 'Bern', 'Lausanne', 'Rue de la gare 1, 1000 Lausanne')"
    ),
    destination_name: str = Field(
        description="The name of the place of destination to search for can be a city or a station name or an address (e.g. 'Zürich HB', 'Bern', 'Lausanne', 'Rue de la gare 1, 1000 Lausanne')"
    ),
    departure_date: str = Field(description="The date of the trip (e.g. '2025-05-01')"),
    departure_time: str = Field(
        description="The time of the trip (e.g. '12:00')", default="12:00"
    ),
) -> dict:
    """get all available SBB trips between two places after a given departure date and time."""
    async with httpx.AsyncClient(
        headers={"Content-Type": "application/json"}, timeout=15
    ) as client:
        # get places
        async with asyncio.TaskGroup() as tg:
            get_places_origin = tg.create_task(get_places(client, origin_name))
            get_places_destination = tg.create_task(
                get_places(client, destination_name)
            )

        origin_places = get_places_origin.result()
        destination_places = get_places_destination.result()

        if isinstance(origin_places, dict) and origin_places.get("error") is not None:
            return origin_places

        if (
            isinstance(destination_places, dict)
            and destination_places.get("error") is not None
        ):
            return destination_places

        origin_id = origin_places[0].id
        destination_id = destination_places[0].id

        ctx.report_progress(33, 100)

        # get the trips
        trips = await _get_trips(
            client, origin_id, destination_id, departure_date, departure_time
        )

        if trips.get("error") is not None:
            return trips

        ctx.report_progress(66, 100)

        # get the trip prices

        return trips

        # get the trip prices


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


if __name__ == "__main__":
    # mcp.run()
    from unittest.mock import Mock

    ctx = Mock()
    res = asyncio.run(get_trips(ctx, "Zürich HB", "Bern", "2025-05-01", "12:00"))
    print(res)
