get_places = """
query GetPlaces($input: PlaceInput, $language: LanguageEnum!) {
    places(input: $input, language: $language) {
    id
    name
    __typename
    }
}
"""

get_trips = """
query getTrips($input: TripInput!, $pagingCursor: String, $language: LanguageEnum!) {
    trips(tripInput: $input, pagingCursor: $pagingCursor, language: $language) {
    trips {
        ...TripFields
        __typename
    }
    paginationCursor {
        previous
        next
        __typename
    }
    __typename
    }
}

fragment NoticesFields on Notice {
    name
    text {
    template
    arguments {
        type
        values
        __typename
    }
    __typename
    }
    type
    priority
    advertised
    __typename
}

fragment ArrivalDepartureFields on ScheduledStopPointDetail {
    time
    delay
    delayText
    quayFormatted
    quayChanged
    quayChangedText
    __typename
}

fragment BoardingAFields on AccessibilityBoardingAlighting {
    limitation
    name
    description
    assistanceService {
    template
    arguments {
        type
        values
        __typename
    }
    __typename
    }
    __typename
}

fragment ServiceProductFields on ServiceProduct {
    name
    line
    number
    vehicleMode
    vehicleSubModeShortName
    corporateIdentityIcon
    corporateIdentityPictogram
    __typename
}

fragment SituationFields on PTSituation {
    cause
    broadcastMessages {
    id
    priority
    title
    detail
    detailShort
    distributionPeriod {
        startDate
        endDate
        __typename
    }
    audiences {
        urls {
        name
        url
        __typename
        }
        __typename
    }
    __typename
    }
    affectedStopPointFromIdx
    affectedStopPointToIdx
    __typename
}

fragment TripStatusFields on TripStatus {
    alternative
    alternativeText
    cancelled
    cancelledText
    partiallyCancelled
    delayed
    delayedUnknown
    quayChanged
    __typename
}

fragment TripFields on Trip {
    id
    legs {
    duration
    id
    ... on AccessLeg {
        __typename
        duration
        distance
        start {
        __typename
        id
        name
        }
        end {
        __typename
        id
        name
        }
    }
    ... on PTConnectionLeg {
        __typename
        duration
        start {
        __typename
        id
        name
        }
        end {
        __typename
        id
        name
        }
        notices {
        ...NoticesFields
        __typename
        }
    }
    ... on AlternativeModeLeg {
        __typename
        mode
        duration
    }
    ... on PTRideLeg {
        __typename
        duration
        start {
        __typename
        id
        name
        }
        end {
        __typename
        id
        name
        }
        arrival {
        ...ArrivalDepartureFields
        __typename
        }
        departure {
        ...ArrivalDepartureFields
        __typename
        }
        serviceJourney {
        id
        stopPoints {
            place {
            id
            name
            __typename
            }
            occupancy {
            firstClass
            secondClass
            __typename
            }
            accessibilityBoardingAlighting {
            ...BoardingAFields
            __typename
            }
            stopStatus
            stopStatusFormatted
            delayUndefined
            __typename
        }
        serviceProducts {
            ...ServiceProductFields
            routeIndexFrom
            routeIndexTo
            __typename
        }
        direction
        serviceAlteration {
            cancelled
            cancelledText
            partiallyCancelled
            partiallyCancelledText
            redirected
            redirectedText
            reachable
            reachableText
            delayText
            unplannedStopPointsText
            quayChangedText
            __typename
        }
        situations {
            ...SituationFields
            __typename
        }
        notices {
            ...NoticesFields
            __typename
        }
        quayTypeName
        quayTypeShortName
        __typename
        }
    }
    __typename
    }
    situations {
    ...SituationFields
    __typename
    }
    notices {
    ...NoticesFields
    __typename
    }
    valid
    isBuyable
    summary {
    duration
    arrival {
        ...ArrivalDepartureFields
        __typename
    }
    arrivalWalk
    lastStopPlace {
        __typename
        id
        name
        canton
    }
    tripStatus {
        ...TripStatusFields
        __typename
    }
    departure {
        ...ArrivalDepartureFields
        __typename
    }
    departureWalk
    firstStopPlace {
        __typename
        id
        name
        canton
    }
    product {
        ...ServiceProductFields
        __typename
    }
    direction
    occupancy {
        firstClass
        secondClass
        __typename
    }
    tripStatus {
        ...TripStatusFields
        __typename
    }
    boardingAlightingAccessibility {
        ...BoardingAFields
        __typename
    }
    international
    __typename
    }
    searchHint
    __typename
}
"""

get_trips_prices = """
    query TripPrices($input: TripPricesQueryInput!) {
  tripPrices(input: $input) {
    tripId
    tripPrices {
      price {
        amount
        currency
        vats {
          amount
          currency
          taxId
        }
      }
      productId
      travelClass
      afterSaleFlexibility
    }
  }
}
    """
