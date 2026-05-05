# logslice

Stream and filter large log files with regex patterns and time-range queries.

## Installation

```bash
pip install logslice
```

## Usage

```bash
# Filter logs by regex pattern
logslice --pattern "ERROR|CRITICAL" /var/log/app.log

# Filter logs within a time range
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" /var/log/app.log

# Combine pattern and time-range filters
logslice --pattern "timeout" --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" /var/log/app.log
```

You can also use logslice as a Python library:

```python
from logslice import LogStream

stream = LogStream("/var/log/app.log")

for line in stream.filter(pattern=r"ERROR|CRITICAL", start="2024-01-15 08:00:00"):
    print(line)
```

## Features

- Streams large log files without loading them fully into memory
- Filter by regex patterns
- Filter by start and end timestamps
- Supports plain text and gzipped log files
- Simple CLI and Python API

## Requirements

- Python 3.8+

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/yourname/logslice).