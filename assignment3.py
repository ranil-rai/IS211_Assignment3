
import argparse
import csv
import re
import datetime
from collections import Counter, defaultdict
from urllib.request import urlopen


def download_log_file(url: str) -> str:
    try:
        with urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        raise e


def process_file(file_contents: str) -> list:
    log_data = []
    for row in csv.reader(file_contents.splitlines()):
        path, datetime_str, user_agent, _, _ = row
        datetime_accessed = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        log_data.append((path, datetime_accessed, user_agent))
    return log_data


def calculate_image_hits(log_data: list) -> float:
    total_hits = len(log_data)
    image_hits = sum(1 for path, _, _ in log_data if re.search(r'\\.(jpg|gif|png)$', path, re.I))
    return (image_hits / total_hits) * 100 if total_hits > 0 else 0


def find_most_popular_browser(log_data: list) -> str:
    browser_counts = Counter()
    browser_regex = re.compile(r'(Firefox|Chrome|Internet Explorer|Safari)', re.I)
    
    for _, _, user_agent in log_data:
        match = browser_regex.search(user_agent)
        if match:
            browser_counts[match.group(1)] += 1
    
    most_common_browser = browser_counts.most_common(1)
    return most_common_browser[0][0] if most_common_browser else "No browser information available"


def hits_per_hour(log_data: list) -> dict:
    hits_by_hour = defaultdict(int)
    for _, datetime_accessed, _ in log_data:
        hits_by_hour[datetime_accessed.hour] += 1
    
    sorted_hits_by_hour = sorted(hits_by_hour.items(), key=lambda x: (-x[1], x[0]))
    return sorted_hits_by_hour


def main():
    try:
        url = input("Please enter the URL of the log file to be processed: ")
        file_contents = download_log_file(url)
    except Exception as e:
        print(f"An error occurred while downloading the log file: {str(e)}")
        return
    
    log_data = process_file(file_contents)
    
    image_hit_percent = calculate_image_hits(log_data)
    print(f"Image requests account for {image_hit_percent:.2f}% of all requests")
    
    most_popular_browser = find_most_popular_browser(log_data)
    print(f"The most popular browser is {most_popular_browser}")
    
    sorted_hits_by_hour = hits_per_hour(log_data)
    for hour, hits in sorted_hits_by_hour:
        print(f"Hour {hour} has {hits} hits")


if __name__ == "__main__":
    main()
