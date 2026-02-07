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
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup


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
    
    def __init__(self, delay: float = 2.0, timeout: int = 10):
        """
        Initialize the Google Dork client
        
        Args:
            delay: Minimum delay between requests in seconds
            timeout: Request timeout in seconds
        """
        self.delay = delay
        self.timeout = timeout
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
        """
        Perform a Google search for the given dork query
        
        Args:
            query: Google dork query string
            
        Returns:
            List of results with title, url, and snippet
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
                except Exception as e:
                    continue
            
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
def main(file, target, output, delay, output_csv, output_json, console):
    """
    Google Dork CLI Tool
    
    Perform Google dork searches from a text file with bot detection bypass.
    
    Examples:
        python google_dork_cli.py --file dorks.txt --output results --delay 3
        python google_dork_cli.py -t example.com -f dorks.txt
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
    
    click.echo(f'Found {len(queries)} queries to search')
    if target:
        click.echo(f'Target domain: {target}')
    click.echo(f'Delay between requests: {delay}s')
    click.echo('=' * 50)
    click.echo()
    
    # Perform searches
    client = GoogleDorkClient(delay=delay)
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
