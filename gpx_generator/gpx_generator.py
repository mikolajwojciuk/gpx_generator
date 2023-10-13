import googlemaps
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint
import os
from typing import TypeAlias, List, Tuple

Gmaps: TypeAlias = googlemaps.client.Client


class GPXRoute:
    def __init__(self, gmaps: Gmaps) -> None:
        self.gmaps = gmaps

    def generate_directions(
        self,
        origin: str,
        destination: str,
        waypoints: List[str],
        optimize_waypoints: bool = False,
    ):
        self.origin = origin
        self.destination = destination
        self.waypoints = waypoints

        self.raw_directions = self.gmaps.directions(
            origin=self.origin,
            destination=self.destination,
            waypoints=self.waypoints if self.waypoints else None,
            mode="bicycling",
            language="polish",
            units="metric",
            optimize_waypoints=optimize_waypoints,
        )

        self.coordinates = self._get_coordinates()
        self.distance = sum(
            [leg["distance"]["value"] for leg in self.raw_directions[0]["legs"]]
        )
        self.duration = sum(
            [leg["duration"]["value"] for leg in self.raw_directions[0]["legs"]]
        )
        self.gpx = self._generate_gpx()

    def export_gpx(self, route_name: str = "Route") -> None:
        self.gpx.name = route_name
        with open(f"{route_name}.gpx", "w") as file:
            file.write(self.gpx.to_xml())

    def _generate_gpx(self) -> GPX:
        gpx = GPX()
        gpx.description = f"Route from {self.origin} to {self.destination}"

        gpx_track = GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        print(self.coordinates)
        for point in self.coordinates:
            gpx_segment.points.append(GPXTrackPoint(point["lat"], point["lng"]))

        return gpx

    def _get_coordinates(self) -> List[Tuple[float, float]]:
        coordinates = []
        for leg in self.raw_directions[0]["legs"]:
            for n, direction in enumerate(leg["steps"]):
                if n == 0:
                    coordinates.append(direction["start_location"])
                else:
                    coordinates.append(direction["end_location"])
        return coordinates


# TODO
# Zapis i download tymczasowego pliku
# Drugi plik z analizą wczytanego GPXa
