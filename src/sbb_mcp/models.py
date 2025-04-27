from pydantic import BaseModel, Field
from datetime import datetime


class StopPlace(BaseModel):
    id: str = Field(
        description="The stop place id (e.g. '8503000' for Zurich HB. can be found by calling get_places)"
    )
    name: str = Field(description="The stop place name (e.g. 'Zürich HB')")
    canton: str | None = Field(
        default=None, description="Initial of the canton of the stop place (e.g. 'ZH')"
    )


class ScheduleStopPointDetail(BaseModel):
    time: datetime = Field(description="The date and time of the stop in isoformat")
    delay: int = Field(description="The delay at the stop in minutes 0 means on time")


class ServiceProduct(BaseModel):
    name: str = Field(
        description="The name of the service product (e.g. 'RE 1', 'IC 1')"
    )
    category: str | None = Field(
        default=None, description="The category of the service product"
    )
    # TODO: vehicleMode could be nice to check here if it's not train or something


class TripSummary(BaseModel):
    duration: int = Field(description="The duration of the trip in minutes")
    arrival: ScheduleStopPointDetail = Field(
        description="The arrival stop point detail"
    )
    arrival_walk: int = Field(
        description="The walk time to the arrival stop in minutes", alias="arrivalWalk"
    )
    last_stop_place: StopPlace = Field(
        description="The last stop of the trip", alias="lastStopPlace"
    )
    # trip_status could be nice to add here with changed quay, delay, cancelled, etc...
    departure: ScheduleStopPointDetail = Field(
        description="The departure stop point detail"
    )
    departure_walk: int = Field(
        description="The walk time to the departure stop in minutes",
        alias="departureWalk",
    )
    first_stop_place: StopPlace = Field(
        description="The first stop of the trip", alias="firstStopPlace"
    )
    product: ServiceProduct = Field(description="The product of the trip")
    direction: str = Field(description="The direction (final stop of the trip)")


class PTRideLeg(BaseModel):
    duration: int = Field(description="The duration of the leg in minutes")
    id: str = Field(description="The leg id (e.g. '0' for the first leg)")
    start: StopPlace = Field(description="The start stop place")
    end: StopPlace = Field(description="The end stop place")
    arrival: ScheduleStopPointDetail = Field(
        description="The arrival stop point detail"
    )
    departure: ScheduleStopPointDetail = Field(
        description="The departure stop point detail"
    )


class Trip(BaseModel):
    id: str = Field(
        description="The trip id (e.g. '3HA...' can be found by calling get_trips)"
    )
    legs: list[PTRideLeg] = Field(description="The legs of the trip")
    summary: TripSummary = Field(description="The summary of the trip")
