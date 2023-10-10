import argparse
import logging
import os

import plotly.express as px

from .Feed import Feed
from .FeedElaborator import FeedElaborator
from .utils import DIRS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def plot(trips_data, route_long_names, route_stop_names, out_file_path, outputs):
    logger.debug("Chart setup")
    axis_labels = {"time": "Time", "stop_name": "Stop"}

    figure = px.line(
        trips_data,
        x="time",
        y="stop_name",
        color="trip_id",
        markers=True,
        title=f"{route_long_names}",
        labels=axis_labels,
    )
    figure.update_yaxes(
        ticks="outside",
        gridcolor="DarkGray",
        griddash="dot",
        type="category",
        categoryorder="array",
        categoryarray=route_stop_names,
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )
    figure.update_xaxes(
        ticks="outside",
        gridcolor="DarkGray",
        griddash="dash",
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )
    figure.update_traces(line=dict(width=2))
    figure.update_layout(plot_bgcolor="rgba(0,0,0,0)")

    width = max(1300, len(trips_data.index) * 0.75)
    height = width * 0.6

    logger.info("Generating output charts")

    for output in outputs:
        match output:
            case "html":
                figure.write_html(f"{out_file_path}.html")
            case "png":
                figure.write_image(f"{out_file_path}.png", width=width, height=height)
            case "svg":
                figure.write_image(f"{out_file_path}.svg", width=width, height=height)


def make_dirs():
    [os.makedirs(dir, exist_ok=True) for dir in ["assets", "output"]]


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="gtfs-marey",
        description="Generate a Marey Chart for the given GTFS route",
    )
    parser.add_argument("--feed", nargs=1, required=True, help="feed path or url")
    parser.add_argument(
        "--route_names",
        nargs="+",
        required=True,
        help="route name referencing 'route_short_name' value in GTFS",
    )
    parser.add_argument(
        "--outputs",
        nargs="+",
        required=True,
        choices=["html", "svg", "png"],
        help="output type",
    )
    parser.add_argument(
        "--days",
        nargs="+",
        required=True,
        help="day of the week to consider in the chart creation",
    )
    parser.add_argument("--verbose", action="store_true", help="Turn on verbose mode")

    logger.debug("Arguments initialized")

    return parser


def main():
    make_dirs()
    parser = setup_parser()
    args = parser.parse_args()
    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG)
    logger.info(f"Received following arguments: {args}")

    feed = Feed(args.feed[0], args.route_names)
    elaborator = FeedElaborator(feed.get())
    trips_data = elaborator.trips_running_on(args.days)

    route_stop_names = elaborator.route_stop_names()
    route_long_names = ",".join(elaborator.route_long_names())
    route_short_names = "_".join(args.route_names)

    out_file_path = (
        f"{DIRS['OUTPUT']}/{feed.feed_name}-{route_short_names}-{'_'.join(args.days)}"
    )
    plot(trips_data, route_long_names, route_stop_names, out_file_path, args.outputs)

    logger.info("Terminating")
