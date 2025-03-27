# CCLoad - Concurrent HTTP Load Testing Tool

A powerful, Python-based HTTP load testing tool designed to evaluate web application performance under concurrent request scenarios.

## Features

- **High Performance**: Built with asyncio for efficient concurrent HTTP requests
- **Detailed Metrics**: Comprehensive performance metrics including response times, TTFB, TTLB, and more
- **Flexible Testing Options**:
  - Single URL testing
  - Bulk URL testing from files
  - Script-based complex test scenarios
  - Distributed load testing across multiple workers
- **Multiple HTTP Methods**: Support for GET, POST, PUT and other common methods
- **Custom Headers & Data**: Add custom headers and JSON payloads to requests
- **Export Options**: Export metrics in JSON, CSV, Prometheus, or InfluxDB formats
- **Included Mock Server**: Test locally with an integrated heavy-content mock server

## Installation

Requires Python 3.12 or higher.

```bash
# Clone the repository
git clone https://github.com/matheusalb/load-tester.git
cd load-tester/ccload

# Install with poetry
poetry install

# Or install with pip
pip install .
```

## Usage

### Basic URL Testing

Test a single URL with 10 concurrent connections and 100 total requests:

```bash
ccload https://example.com -c 10 -n 100
```

### Testing with Different HTTP Methods

```bash
ccload https://api.example.com/users -m POST --json '{"name": "Test User"}'
```

### Testing with Custom Headers

```bash
ccload https://api.example.com --headers '{"Authorization": "Bearer token123"}'
```

### Testing Multiple URLs from File

```bash
ccload -f urls.txt -c 5 -n 20
```

### Script-based Testing

Create a JSON script with different request configurations:

```bash
ccload -s test_script.json --export json --output results.json
```

### Distributed Load Testing

```bash
# Start distributed workers and run test
ccload https://example.com -c 100 -n 1000 --distributed --distributed-workers 4

# Or use existing workers
ccload https://example.com -c 100 -n 1000 --distributed --workers "http://worker1:8001,http://worker2:8001"
```

## Local Testing with Mock Server

The included mock server generates heavy content pages for local testing:

```bash
# Start the mock server
python mock_server/main.py

# Run a test against it
ccload http://localhost:8000 -c 5 -n 20
```

## Development

```bash
# Setup development environment
cd ccload
poetry install

# Run tests
poetry run pytest
```

## License

MIT

## Author

Matheus Albuquerque (mvca@cin.ufpe.br)