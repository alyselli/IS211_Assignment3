import argparse
import csv
import io
import re
from collections import Counter
from datetime import datetime

import requests


def download_log(url):
    """Download the web log CSV file from the supplied URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def process_log(csv_text):
    """Process the CSV file and store the data in memory."""
    log_data = []

    csv_file = io.StringIO(csv_text)
    reader = csv.reader(csv_file)

    for row in reader:
        if len(row) >= 5:
            log_data.append(row)

    return log_data


def get_image_percentage(log_data):
    """Calculate the percentage of requests for image files."""
    image_regex = re.compile(r"\.(jpg|gif|png)$", re.IGNORECASE)

    image_count = 0

    for row in log_data:
        path = row[0].strip()

        if image_regex.search(path):
            image_count += 1

    if len(log_data) == 0:
        return 0

    return (image_count / len(log_data)) * 100


def get_most_popular_browser(log_data):
    """Determine the most popular browser."""
    browser_counts = Counter()

    for row in log_data:
        user_agent = row[2].strip()

        if re.search(r"Chrome", user_agent, re.IGNORECASE):
            browser_counts["Chrome"] += 1

        elif re.search(r"Firefox", user_agent, re.IGNORECASE):
            browser_counts["Firefox"] += 1

        elif re.search(r"MSIE|Trident", user_agent, re.IGNORECASE):
            browser_counts["Internet Explorer"] += 1

        elif re.search(r"Safari", user_agent, re.IGNORECASE):
            browser_counts["Safari"] += 1

    if not browser_counts:
        return "Unknown"

    return browser_counts.most_common(1)[0][0]


def get_hourly_hits(log_data):
    """Count requests for each hour of the day."""
    hours = {hour: 0 for hour in range(24)}

    for row in log_data:
        date_string = row[1].strip()

        try:
            date_accessed = datetime.strptime(
                date_string,
                "%Y-%m-%d %H:%M:%S"
            )

            hours[date_accessed.hour] += 1

        except ValueError:
            continue

    return sorted(
        hours.items(),
        key=lambda item: item[1],
        reverse=True
    )


def main():
    """Run the web log processing program."""
    parser = argparse.ArgumentParser(
        description="IS211 Assignment 3 - Text Processing"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="URL of the web log CSV file"
    )

    args = parser.parse_args()

    try:
        csv_text = download_log(args.url)

    except requests.RequestException as error:
        print("Error downloading web log:")
        print(error)
        return

    log_data = process_log(csv_text)

    image_percentage = get_image_percentage(log_data)

    print(
        f"Image requests account for "
        f"{image_percentage:.1f}% of all requests"
    )

    popular_browser = get_most_popular_browser(log_data)

    print(
        f"The most popular browser is "
        f"{popular_browser}"
    )

    print("\nHits by hour:")

    for hour, hits in get_hourly_hits(log_data):
        print(
            f"Hour {hour:02d} has {hits} hits"
        )


if __name__ == "__main__":
    main()

    
