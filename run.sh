#!/bin/bash
# Google Dork CLI - Linux/Mac Bash Wrapper

echo ""
echo "🔍 Google Dork CLI Tool"
echo "========================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python3 first"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import requests, click, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing dependencies"
        exit 1
    fi
fi

echo "Choose an option:"
echo "1. Basic search (fastest)"
echo "2. Search with stealth (recommended)"
echo "3. Search with proxy support (advanced)"
echo "4. Search and preview results"
echo "5. Custom command"
echo "6. Exit"
echo ""

read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo "Running basic search..."
        python3 google_dork_cli.py -f dorks.txt
        ;;
    2)
        echo "Running search with stealth (5s delay)..."
        python3 google_dork_cli.py -f dorks.txt -d 5
        ;;
    3)
        echo "Running search with proxies..."
        python3 advanced.py -f dorks.txt --proxies proxies.txt -d 3
        ;;
    4)
        echo "Running search with console output..."
        python3 google_dork_cli.py -f dorks.txt --console
        ;;
    5)
        read -p "Enter custom command: " cmd
        python3 google_dork_cli.py $cmd
        ;;
    6)
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done! Check the results_*.csv and results_*.json files"
