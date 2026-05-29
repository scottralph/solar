#!/usr/bin/env python3
"""Solar radio condition forecast — entry point."""

import argparse
import json
import sys

from fetchers import noaa_swpc, spaceweather, spaceweatherlive
import report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2-3 day radio condition forecast.")
    parser.add_argument("--json", action="store_true", help="Dump raw fetched data as JSON instead of a report.")
    args = parser.parse_args()

    print("Fetching data…", file=sys.stderr)

    noaa = noaa_swpc.fetch_all()
    swcom = spaceweather.fetch_all()
    swlive = spaceweatherlive.fetch_all()

    if args.json:
        print(json.dumps({"noaa": noaa, "spaceweather": swcom, "spaceweatherlive": swlive}, indent=2, default=str))
        return

    print(report.build(noaa, swcom, swlive))


if __name__ == "__main__":
    main()
