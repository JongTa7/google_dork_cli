#!/usr/bin/env python3
"""
Advanced Google Dork CLI Tool
With proxy support, caching, and advanced bot detection bypass
"""

import os
import json
import csv
import time
import random
import click
import requests
from urllib.parse import quote, urlparse
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ProxyRotation:
    """Manages proxy rotation for requests"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_list = proxy_list or []
        self.current_index = 0
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation or None if no proxies"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        
        return self._parse_proxy(proxy)
    
    @staticmethod
    def _parse_proxy(proxy_url: str) -> Dict:
        """Parse proxy URL and return proxy dict for requests"""
        if not proxy_url.startswith(('http://', 'https://', 'socks5://')):
            proxy_url = 'http://' + proxy_url
        
        return {
            'http': proxy_url,
            'https': proxy_url,
        }
    
    def load_from_file(self, file_path: str):
        """Load proxies from file (one per line)"""
        try:
            with open(file_path, 'r') as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
            click.echo(f'✓ Loaded {len(self.proxy_list)} proxies')
        except Exception as e:
            click.echo(f'Error loading proxies: {str(e)}', err=True)


class CacheManager:
    """Manages caching of search results"""
    
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_file(self, query: str) -> str:
        """Generate cache file path for query"""
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return os.path.join(self.cache_dir, f'{query_hash}.json')
    
    def get(self, query: str) -> Optional[List[Dict]]:
        """Get cached results for query"""
        cache_file = self.get_cache_file(query)
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if datetime.now().timestamp() - data['timestamp'] < 86400:  # 24 hour cache
                        return data['results']
        except Exception:
            pass
        return None
    
    def set(self, query: str, results: List[Dict]):
        """Cache results for query"""
        cache_file = self.get_cache_file(query)
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'query': query,
                    'results': results,
                    'timestamp': datetime.now().timestamp(),
                }, f)
        except Exception as e:
            click.echo(f'Cache write error: {str(e)}', err=True)


class AdvancedGoogleDorkClient:
    """Advanced Google Dork client with proxy and cache support"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    ]
    
    REFERERS = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://www.yahoo.com/',
        'https://duckduckgo.com/',
        'https://www.startpage.com/',
    ]
    
    def __init__(self, delay: float = 2.0, timeout: int = 10, use_cache: bool = False, 
                 proxies: ProxyRotation = None):
        self.delay = delay
        self.timeout = timeout
        self.proxies = proxies or ProxyRotation()
        self.cache = CacheManager() if use_cache else None
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy for transient failures
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["GET"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_random_headers(self) -> Dict:
        """Generate random headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Referer': random.choice(self.REFERERS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
    
    def search(self, query: str) -> List[Dict[str, str]]:
        """Perform search with cache and proxy support"""
        
        # Check cache first
        if self.cache:
            cached = self.cache.get(query)
            if cached:
                return cached
        
        # Add delay
        time.sleep(self.delay + random.uniform(0, 1))
        
        results = []
        try:
            url = 'https://www.google.com/search'
            params = {
                'q': query,
                'num': 10,
                'start': 0,
            }
            
            headers = self._get_random_headers()
            proxy = self.proxies.get_next_proxy() if self.proxies else None
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                proxies=proxy,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse results
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for result in soup.find_all('div', class_='g'):
                try:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('span', class_='st')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url_str = link_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else 'N/A'
                        
                        if url_str and 'google.com' not in url_str and url_str.startswith('http'):
                            results.append({
                                'title': title,
                                'url': url_str,
                                'snippet': snippet,
                                'domain': urlparse(url_str).netloc,
                            })
                except Exception:
                    continue
            
            # Cache results
            if self.cache:
                self.cache.set(query, results)
            
        except Exception as e:
            click.echo(f'Search error for "{query}": {str(e)}', err=True)
        
        return results
    
    def search_multiple(self, queries: List[str], progress: bool = True) -> Dict:
        """Search multiple queries with progress tracking"""
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
    """Save results to CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Query', 'Title', 'URL', 'Domain', 'Snippet'])
        
        for query, items in results.items():
            for item in items:
                writer.writerow([
                    query,
                    item.get('title', ''),
                    item.get('url', ''),
                    item.get('domain', ''),
                    item.get('snippet', ''),
                ])


def save_to_json(results: Dict[str, List[Dict]], output_file: str):
    """Save results to JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


@click.command(no_args_is_help=True)
@click.option('--file', '-f', type=click.Path(exists=True), required=True,
              help='Dork queries file')
@click.option('--target', '-t', type=str, default=None,
              help='Target domain (site:example.com)')
@click.option('--output', '-o', type=click.Path(), default='results',
              help='Output file prefix')
@click.option('--delay', '-d', type=float, default=2.0,
              help='Delay between requests (seconds)')
@click.option('--proxies', '-p', type=click.Path(exists=True), default=None,
              help='Path to proxies file (one per line)')
@click.option('--cache', is_flag=True, default=False,
              help='Enable result caching')
@click.option('--csv', 'output_csv', is_flag=True, default=True,
              help='Save to CSV')
@click.option('--json', 'output_json', is_flag=True, default=True,
              help='Save to JSON')
@click.option('--console', is_flag=True, default=False,
              help='Print to console')
def main(file, target, output, delay, proxies, cache, output_csv, output_json, console):
    """
    Advanced Google Dork CLI Tool with Proxy & Cache Support
    """
    click.echo('🔍 Advanced Google Dork CLI Tool')
    click.echo('=' * 50)
    
    # Load queries
    try:
        with open(file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    except Exception as e:
        click.echo(f'Error reading file: {str(e)}', err=True)
        return
    
    if not queries:
        click.echo('No queries found', err=True)
        return
    
    # Add target domain to queries if specified
    if target:
        queries = [f'site:{target} {query}' for query in queries]
    
    # Setup proxy rotation
    proxy_rotation = ProxyRotation()
    if target:
        click.echo(f'Target: {target}')
    if proxies:
        proxy_rotation.load_from_file(proxies)
    
    click.echo(f'Queries: {len(queries)}')
    click.echo(f'Delay: {delay}s')
    click.echo(f'Cache: {"Enabled" if cache else "Disabled"}')
    if proxies:
        click.echo(f'Proxies: {len(proxy_rotation.proxy_list)}')
    click.echo('=' * 50)
    click.echo()
    
    # Perform searches
    client = AdvancedGoogleDorkClient(
        delay=delay,
        use_cache=cache,
        proxies=proxy_rotation
    )
    results = client.search_multiple(queries)
    
    # Statistics
    total_results = sum(len(items) for items in results.values())
    click.echo()
    click.echo('=' * 50)
    click.echo(f'✓ Complete! Found {total_results} results')
    click.echo('=' * 50)
    click.echo()
    
    # Console output
    if console:
        click.echo('Results:')
        for query, items in results.items():
            click.echo(f'\nQuery: {query}')
            for i, item in enumerate(items, 1):
                click.echo(f'  {i}. {item["title"][:60]}...')
                click.echo(f'     {item["url"][:70]}...')
    
    # Save files
    if output_csv:
        csv_file = f'{output}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        save_to_csv(results, csv_file)
        click.echo(f'✓ CSV: {csv_file}')
    
    if output_json:
        json_file = f'{output}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        save_to_json(results, json_file)
        click.echo(f'✓ JSON: {json_file}')


if __name__ == '__main__':
    main()
