#!/usr/bin/env python3
"""
Google Dork CLI Tool
Performs Google dork searches with bot detection bypass using user-agent rotation
"""

import os
import json
import csv
import time
import random
import click
import requests
from urllib.parse import quote
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup


DEFAULT_BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
DEFAULT_SEARXNG_ENDPOINT = "http://localhost:8080"


def load_config(path: str) -> Dict:
    if not path:
        return {}
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_config_value(config: Dict, keys: List[str], default=None):
    value = config
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def resolve_bing_config(config_path: str) -> Dict[str, Optional[str]]:
    config = load_config(config_path)
    api_key = os.getenv("BING_API_KEY") or get_config_value(config, ["bing", "api_key"])
    endpoint = os.getenv("BING_ENDPOINT") or get_config_value(
        config, ["bing", "endpoint"], DEFAULT_BING_ENDPOINT
    )
    if not endpoint:
        endpoint = DEFAULT_BING_ENDPOINT
    return {"api_key": api_key, "endpoint": endpoint}


def resolve_searxng_config(config_path: str) -> Dict[str, Optional[str]]:
    config = load_config(config_path)
    api_key = os.getenv("SEARXNG_API_KEY") or get_config_value(config, ["searxng", "api_key"])
    endpoint = os.getenv("SEARXNG_ENDPOINT") or get_config_value(
        config, ["searxng", "endpoint"], DEFAULT_SEARXNG_ENDPOINT
    )
    if not endpoint:
        endpoint = DEFAULT_SEARXNG_ENDPOINT
    return {"api_key": api_key, "endpoint": endpoint}


class GoogleDorkClient:
    """Client for performing Google dork searches with user-agent rotation"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    ]
    
    REFERERS = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://www.yahoo.com/',
        'https://duckduckgo.com/',
    ]
    
    def __init__(
        self,
        delay: float = 2.0,
        timeout: int = 10,
        engine: str = "google",
        bing_api_key: Optional[str] = None,
        bing_endpoint: Optional[str] = None,
        searxng_api_key: Optional[str] = None,
        searxng_endpoint: Optional[str] = None,
    ):
        """
        Initialize the search client
        
        Args:
            delay: Minimum delay between requests in seconds
            timeout: Request timeout in seconds
            engine: Search engine to use (google or bing)
            bing_api_key: Bing Web Search API key
            bing_endpoint: Bing Web Search API endpoint
        """
        self.delay = delay
        self.timeout = timeout
        self.engine = engine.lower()
        self.bing_api_key = bing_api_key
        self.bing_endpoint = bing_endpoint or DEFAULT_BING_ENDPOINT
        self.searxng_api_key = searxng_api_key
        self.searxng_endpoint = searxng_endpoint or DEFAULT_SEARXNG_ENDPOINT
        self.session = requests.Session()
        
    def _get_random_headers(self) -> Dict:
        """Generate random headers for the request"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Referer': random.choice(self.REFERERS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search(self, query: str) -> List[Dict[str, str]]:
        if self.engine == "bing":
            return self._search_bing(query)
        if self.engine == "duckduckgo":
            return self._search_duckduckgo(query)
        if self.engine == "searxng":
            return self._search_searxng(query)
        return self._search_google(query)

    def _search_google(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a Google search for the given dork query
        """
        results = []
        
        try:
            # Add random delay to avoid bot detection
            time.sleep(self.delay + random.uniform(0, 1))
            
            # Use Google search with parameters
            url = 'https://www.google.com/search'
            params = {
                'q': query,
                'num': 10,  # Number of results
                'start': 0,
            }
            
            headers = self._get_random_headers()
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse the HTML response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results
            for result in soup.find_all('div', class_='g'):
                try:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('span', class_='st')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else 'N/A'
                        
                        # Skip Google search result pages
                        if url and 'google.com' not in url and url.startswith('http'):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                            })
                except Exception:
                    continue
            
            return results
            
        except requests.exceptions.RequestException as e:
            click.echo(f'Error searching for "{query}": {str(e)}', err=True)
            return []

    def _search_bing(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a Bing search using the Web Search API
        """
        if not self.bing_api_key:
            click.echo('Bing API key is missing. Set BING_API_KEY or config.json.', err=True)
            return []
        
        results = []
        try:
            time.sleep(self.delay + random.uniform(0, 1))
            headers = {
                'Ocp-Apim-Subscription-Key': self.bing_api_key,
                'User-Agent': random.choice(self.USER_AGENTS),
            }
            params = {
                'q': query,
                'count': 10,
                'offset': 0,
            }
            response = self.session.get(
                self.bing_endpoint,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', '') or item.get('description', ''),
                })
            return results
        except requests.exceptions.RequestException as e:
            click.echo(f'Error searching for "{query}": {str(e)}', err=True)
            return []

    def _search_duckduckgo(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a DuckDuckGo search using the HTML endpoint
        """
        results = []
        try:
            time.sleep(self.delay + random.uniform(0, 1))
            url = 'https://duckduckgo.com/html/'
            params = {
                'q': query,
            }
            headers = self._get_random_headers()
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for result in soup.select('div.result'):
                link = result.select_one('a.result__a')
                if not link:
                    continue
                title = link.get_text(strip=True)
                url_str = link.get('href', '')
                snippet_elem = result.select_one('.result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else 'N/A'
                if url_str and url_str.startswith('http'):
                    results.append({
                        'title': title,
                        'url': url_str,
                        'snippet': snippet,
                    })
            return results
        except requests.exceptions.RequestException as e:
            click.echo(f'Error searching for "{query}": {str(e)}', err=True)
            return []

    def _search_searxng(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a SearXNG search using JSON endpoint
        """
        if not self.searxng_endpoint:
            click.echo('SearXNG endpoint is missing. Set SEARXNG_ENDPOINT or config.json.', err=True)
            return []
        
        results = []
        try:
            time.sleep(self.delay + random.uniform(0, 1))
            headers = {
                'User-Agent': random.choice(self.USER_AGENTS),
            }
            base_url = self.searxng_endpoint.rstrip('/')
            url = f'{base_url}/search'
            params = {
                'q': query,
                'format': 'json',
            }
            if self.searxng_api_key:
                params['api_key'] = self.searxng_api_key
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            for item in data.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('content', '') or item.get('snippet', ''),
                })
            return results
        except requests.exceptions.RequestException as e:
            click.echo(f'Error searching for "{query}": {str(e)}', err=True)
            return []
    
    def search_multiple(self, queries: List[str], progress: bool = True) -> Dict[str, List[Dict]]:
        """
        Perform multiple searches
        
        Args:
            queries: List of dork queries
            progress: Show progress bar
            
        Returns:
            Dictionary with query as key and list of results as value
        """
        all_results = {}
        
        if progress:
            with click.progressbar(queries, label='Searching') as iterator:
                for query in iterator:
                    all_results[query] = self.search(query)
        else:
            for query in queries:
                click.echo(f'Searching: {query}')
                all_results[query] = self.search(query)
        
        return all_results


def save_to_csv(results: Dict[str, List[Dict]], output_file: str):
    """Save results to CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Query', 'Title', 'URL', 'Snippet'])
        
        for query, items in results.items():
            for item in items:
                writer.writerow([
                    query,
                    item.get('title', ''),
                    item.get('url', ''),
                    item.get('snippet', ''),
                ])


def save_to_json(results: Dict[str, List[Dict]], output_file: str):
    """Save results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


@click.command(no_args_is_help=True)
@click.option(
    '--file',
    '-f',
    type=click.Path(exists=True),
    required=True,
    help='Path to file containing dork queries (one per line)'
)
@click.option(
    '--target',
    '-t',
    type=str,
    default=None,
    help='Target domain to prepend (site:example.com)'
)
@click.option(
    '--engine',
    '-e',
    type=click.Choice(['google', 'bing', 'duckduckgo', 'searxng'], case_sensitive=False),
    default='google',
    help='Search engine to use: google, bing, duckduckgo, or searxng'
)
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=False),
    default='config.json',
    help='Path to config.json for API keys. Default: config.json'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    default='results',
    help='Output file prefix (without extension). Default: results'
)
@click.option(
    '--delay',
    '-d',
    type=float,
    default=2.0,
    help='Minimum delay between requests in seconds. Default: 2.0'
)
@click.option(
    '--csv',
    'output_csv',
    is_flag=True,
    default=True,
    help='Save results to CSV file'
)
@click.option(
    '--json',
    'output_json',
    is_flag=True,
    default=True,
    help='Save results to JSON file'
)
@click.option(
    '--console',
    is_flag=True,
    default=False,
    help='Print results to console'
)
def main(file, target, engine, config, output, delay, output_csv, output_json, console):
    """
    Google Dork CLI Tool
    
    Perform Google dork searches from a text file with bot detection bypass.
    
    Examples:
        python google_dork_cli.py --file dorks.txt --output results --delay 3
        python google_dork_cli.py -t example.com -f dorks.txt
        python google_dork_cli.py -e bing -c config.json -f dorks.txt
        python google_dork_cli.py -e duckduckgo -f dorks.txt
        python google_dork_cli.py -e searxng -c config.json -f dorks.txt
    """
    click.echo('🔍 Google Dork CLI Tool')
    click.echo('=' * 50)
    
    # Read dork queries from file
    try:
        with open(file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    except Exception as e:
        click.echo(f'Error reading file: {str(e)}', err=True)
        return
    
    if not queries:
        click.echo('No queries found in file', err=True)
        return
    
    # Add target domain to queries if specified
    if target:
        queries = [f'site:{target} {query}' for query in queries]
    
    engine = engine.lower()
    bing_config = resolve_bing_config(config)
    searxng_config = resolve_searxng_config(config)
    if engine == 'bing' and not bing_config['api_key']:
        click.echo('Missing Bing API key. Set BING_API_KEY or update config.json.', err=True)
        return
    if engine == 'searxng' and not searxng_config['endpoint']:
        click.echo('Missing SearXNG endpoint. Set SEARXNG_ENDPOINT or update config.json.', err=True)
        return
    
    click.echo(f'Found {len(queries)} queries to search')
    click.echo(f'Engine: {engine}')
    if target:
        click.echo(f'Target domain: {target}')
    click.echo(f'Delay between requests: {delay}s')
    click.echo('=' * 50)
    click.echo()
    
    # Perform searches
    client = GoogleDorkClient(
        delay=delay,
        engine=engine,
        bing_api_key=bing_config['api_key'],
        bing_endpoint=bing_config['endpoint'],
        searxng_api_key=searxng_config['api_key'],
        searxng_endpoint=searxng_config['endpoint']
    )
    results = client.search_multiple(queries)
    
    # Calculate statistics
    total_results = sum(len(items) for items in results.values())
    click.echo()
    click.echo('=' * 50)
    click.echo(f'✓ Search completed!')
    click.echo(f'Total results found: {total_results}')
    click.echo('=' * 50)
    click.echo()
    
    # Print console output if requested
    if console:
        click.echo('Results:')
        click.echo()
        for query, items in results.items():
            click.echo(f'Query: {query}')
            click.echo(f'Results: {len(items)}')
            for i, item in enumerate(items, 1):
                click.echo(f'  {i}. {item["title"]}')
                click.echo(f'     URL: {item["url"]}')
                click.echo(f'     Snippet: {item["snippet"][:100]}...')
            click.echo()
    
    # Save to files
    if output_csv:
        csv_file = f'{output}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        try:
            save_to_csv(results, csv_file)
            click.echo(f'✓ CSV results saved to: {csv_file}')
        except Exception as e:
            click.echo(f'Error saving CSV: {str(e)}', err=True)
    
    if output_json:
        json_file = f'{output}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        try:
            save_to_json(results, json_file)
            click.echo(f'✓ JSON results saved to: {json_file}')
        except Exception as e:
            click.echo(f'Error saving JSON: {str(e)}', err=True)


if __name__ == '__main__':
    main()
