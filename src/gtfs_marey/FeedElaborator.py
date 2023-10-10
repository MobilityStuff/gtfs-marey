import logging
from datetime import timedelta

import pandas as pd

from .utils import DIRS, drop_all_columns_except

logger = logging.getLogger(__name__)


class FeedElaborator:
    def __init__(self, feed):
        self.feed = feed

    def _route_stops(self):
        """Ordered list of stops for the chosen route

        The longest trip (i.e. the trip with the highest number of stops) is chosen for the scope
        """
        id_of_longest_trip = (
            self.feed.stop_times.groupby("trip_id")["stop_id"].count().idxmax()
        )
        logger.debug(f"Longest trip ID: {id_of_longest_trip}")
        longest_trip = self.feed.stop_times[
            self.feed.stop_times["trip_id"] == id_of_longest_trip
        ]

        stop_names = pd.merge(self.feed.stops, longest_trip, on="stop_id").sort_values(
            "departure_time"
        )
        drop_all_columns_except(
            stop_names, "stop_id", "stop_name", "stop_lat", "stop_lon"
        )
        logger.info(f"Found {len(stop_names.index)} stops for the chosen route")

        return stop_names

    def route_stop_names(self):
        """Flat list of stop names"""
        stops = self._route_stops()
        flat_stops_list = stops["stop_name"].to_list()

        return flat_stops_list

    def route_long_names(self):
        """Flat list of route long names"""
        return self.feed.routes["route_long_name"].to_list()

    def _suitable_trips(self, days):
        """List of trips running on the chosen day(s) of week

        GTFS calendar table is here exploited. Note that we intentionally exclude those services that last less that two weeks, since we are more interested in the normal schedule rather than some exceptional dates. The procedure can anyhow be improved
        """
        calendar = self.feed.calendar
        suitable_calendars = calendar[
            calendar["end_date"] - calendar["start_date"] > timedelta(days=15)
        ]
        conditions = [f"{day}==1" for day in days]
        suitable_calendars = suitable_calendars.query("and ".join(conditions))
        logger.info(f"Found {len(suitable_calendars.index)} suitable calendars")

        suitable_trips = pd.merge(self.feed.trips, suitable_calendars, on="service_id")
        drop_all_columns_except(suitable_trips, "trip_id", "direction_id")
        logger.info(f"Found {len(suitable_trips.index)} suitable trips")

        return suitable_trips

    def trips(self):
        """Short-hand for the trips_running_on method"""
        return trips_running_on(
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        )

    def trips_running_on(self, days):
        """Flat list of trip,stop_time that run on the given day(s)"""
        route_stops = self._route_stops()
        suitable_trips = self._suitable_trips(days)

        # Rename arrival_time and departure_time to time, so to have a flat view of the timetable
        trips_arrival = pd.merge(suitable_trips, self.feed.stop_times)
        trips_arrival = pd.DataFrame(
            trips_arrival, columns=["trip_id", "arrival_time", "stop_id"]
        ).rename(columns={"arrival_time": "time"})
        trips_departure = pd.merge(suitable_trips, self.feed.stop_times)
        trips_departure = pd.DataFrame(
            trips_departure,
            columns=["trip_id", "departure_time", "stop_id", "direction_id"],
        ).rename(columns={"departure_time": "time"})
        trip_stops = pd.concat([trips_arrival, trips_departure])

        trip_stops["time"] = pd.to_datetime(trip_stops["time"], unit="s")
        trip_stops = pd.merge(route_stops, trip_stops, on="stop_id")

        trips = trip_stops.sort_values(by="time", ignore_index=True)

        return trips
