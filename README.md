# Google Dork CLI Tool

A Python command-line tool that runs Google dork queries from a text file and saves results to CSV and JSON.

## Features

- User-agent rotation and request delays
- Batch processing from a file
- CSV and JSON output
- Optional console output
- Target a specific domain with `-t` (adds `site:domain`)

## Installation

```bash
pip install -r requirements.txt
```

If you are on Kali with Python 3.13/3.14, this project avoids `lxml` so you should not see build errors.

## Prepare Your Query File

Create a text file with one query per line:

```
site:github.com password
inurl:admin login
filetype:sql database
```

## Usage

### Basic

```bash
python google_dork_cli.py -f dorks.txt
```

### Common Options

```bash
# Target a specific domain
python google_dork_cli.py -t example.com -f dorks.txt

# Custom output prefix
python google_dork_cli.py -f dorks.txt -o my_results

# Increase delay between requests
python google_dork_cli.py -f dorks.txt -d 5

# Print results to console
python google_dork_cli.py -f dorks.txt --console

# Combine multiple options
python google_dork_cli.py -t example.com -f dorks.txt -o results -d 3 --console
```

### Target Domain (`-t`)

When you use `-t example.com`, each query is prefixed with `site:example.com`.

Example:

```
# Query in file
password

# Actual search
site:example.com password
```

## Command-line Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--file` | `-f` | Path | Required | Path to dork queries file |
| `--target` | `-t` | String | None | Target domain (adds `site:domain`) |
| `--output` | `-o` | Path | results | Output file prefix |
| `--delay` | `-d` | Float | 2.0 | Delay between requests (seconds) |
| `--csv` | | Flag | True | Save to CSV file |
| `--json` | | Flag | True | Save to JSON file |
| `--console` | | Flag | False | Print results to console |

## Output Files

Results are saved with timestamps to avoid overwriting:

- CSV: `results_20240207_143022.csv`
- JSON: `results_20240207_143022.json`

## Example Queries

```
password
api key
private key
secret token
```

## Advanced Version

Use [advanced.py](advanced.py) for proxy rotation and caching:

```bash
python advanced.py -f dorks.txt --cache
python advanced.py -t example.com -f dorks.txt --proxies proxies.txt
```

## Troubleshooting

- If you see rate limiting or CAPTCHA, increase `--delay`.
- If results are empty, verify your query syntax and try later.

## Responsible Use

Use this tool only on authorized targets and in accordance with applicable laws and the search engine's terms of service.

## Support

For issues or improvements:
1. Check the output error messages
2. Review query syntax
3. Try with a single query first
4. Increase delays and try again

## License

Educational use only. Respect all laws and regulations in your jurisdiction.
