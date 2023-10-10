# gtfs-marey

Generate a Marey Chart for the given GTFS route, inspired by [this explanation](http://www.stagniweb.it/cadenz01.htm) (in italian). Beware that the program is not bullet proof and was developed just out of curiosity.

## Install

`pip install git+https://github.com/MobilityStuff/gtfs-marey#egg=gtfs-marey`

Publishing to PyPi won't work until Partridge gets updated, see [here](https://github.com/remix/partridge/issues/82)

## Usage

```
usage: gtfs-marey [-h] --feed FEED --route_names ROUTE_NAMES [ROUTE_NAMES ...] --outputs
                  {html,svg,png} [{html,svg,png} ...] --days DAYS [DAYS ...] [--verbose]

Generate a Marey Chart for the given GTFS route

options:
  -h, --help            show this help message and exit
  --feed FEED           feed path or url
  --route_names ROUTE_NAMES [ROUTE_NAMES ...]
                        route name referencing 'route_short_name' value in GTFS
  --outputs {html,svg,png} [{html,svg,png} ...]
                        output type
  --days DAYS [DAYS ...]
                        day of the week to consider in the chart creation
  --verbose             Turn on verbose mode
```

## Example

`gtfs-marey --feed https://www.trentinotrasporti.it/opendata/google_transit_extraurbano_tte.zip --route_names R35 --output html,png --day monday`

![](docs/example/google_transit_extraurbano_tte-R35-monday.png)

Also see the [interactive page](https://mobilitystuff.github.io/gtfs-marey/example/google_transit_extraurbano_tte-R35-monday.html)

## Things to improve

- Better handling of the calendar schedule
- Position stops based on their distance
- Size of the generated picture
- More meaningful color schema

## Similar tools

[`gtfs-to-chart`](https://github.com/BlinkTagInc/gtfs-to-chart) has a similar scope and is much more production-ready. The major difference is that our tool  shows stops on the opposite axis, and also allows to directly generate a picture out of the elaboration. 