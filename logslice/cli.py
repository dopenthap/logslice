"""Command-line interface for logslice."""

import sys
from datetime import datetime
from typing import Optional

import click

from logslice.filter import filter_lines

DT_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _parse_dt(value: Optional[str], param_name: str) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.strptime(value, DT_FORMAT)
    except ValueError:
        click.echo(f"Error: {param_name} must be in format YYYY-MM-DDTHH:MM:SS", err=True)
        sys.exit(1)


@click.command()
@click.argument("logfile", type=click.Path(exists=True, readable=True), required=False)
@click.option("-p", "--pattern", default=None, help="Regex pattern to filter lines.")
@click.option("-s", "--start", default=None, help="Start datetime (YYYY-MM-DDTHH:MM:SS).")
@click.option("-e", "--end", default=None, help="End datetime (YYYY-MM-DDTHH:MM:SS).")
@click.option("-i", "--ignore-case", is_flag=True, default=False, help="Case-insensitive matching.")
def main(logfile, pattern, start, end, ignore_case):
    """Stream and filter log lines from LOGFILE (or stdin)."""
    start_dt = _parse_dt(start, "--start")
    end_dt = _parse_dt(end, "--end")

    source = open(logfile, "r", encoding="utf-8", errors="replace") if logfile else sys.stdin

    try:
        for line in filter_lines(source, pattern=pattern, start=start_dt, end=end_dt, ignore_case=ignore_case):
            click.echo(line)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    finally:
        if logfile:
            source.close()


if __name__ == "__main__":
    main()
