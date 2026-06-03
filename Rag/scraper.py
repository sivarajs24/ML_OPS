import os
import json
import requests
import time
from datetime import datetime
import xml.etree.ElementTree as ET

# Predefined subreddits to search
TARGET_SUBREDDITS = ["technology", "apps", "android", "apple", "gadgets"]

def scrape_reddit(product_name: str, limit_per_sub: int = 10):
    """
    Scrapes Reddit data by parsing the public RSS feeds.
    This completely bypasses Reddit's 403 blocks and API requirements.
    """
    collected_data = []
    print(f"Scraping Reddit RSS feeds for '{product_name}'...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for sub_name in TARGET_SUBREDDITS:
        try:
            # Construct the RSS search URL
            url = f"https://www.reddit.com/r/{sub_name}/search.rss?q={product_name}&restrict_sr=1"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Parse the XML response
                root = ET.fromstring(response.content)
                # Atom namespace
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                entries = root.findall('atom:entry', ns)
                
                # Limit to the requested amount per sub
                for index, entry in enumerate(entries[:limit_per_sub]):
                    title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ""
                    content = entry.find('atom:content', ns).text if entry.find('atom:content', ns) is not None else ""
                    link = entry.find('atom:link', ns).attrib.get('href', '') if entry.find('atom:link', ns) is not None else ""
                    updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
                    
                    post_data = {
                        "id": f"{sub_name}_{index}",
                        "type": "post",
                        "title": title,
                        "body": content, 
                        "upvotes": 0, # RSS doesn't provide upvotes reliably
                        "subreddit": sub_name,
                        "timestamp": 0,
                        "datetime": updated,
                        "url": link
                    }
                    collected_data.append(post_data)
            else:
                print(f"Error fetching from r/{sub_name}: Status Code {response.status_code}")
                
            # Sleep briefly to avoid being rate-limited
            time.sleep(1.0)
                
        except Exception as e:
            print(f"Error scraping r/{sub_name}: {e}")

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save raw data
    output_path = f"data/raw_{product_name.replace(' ', '_').lower()}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected_data, f, indent=4)
        
    print(f"Scraped {len(collected_data)} items. Saved to {output_path}")
    return collected_data

if __name__ == "__main__":
    # Test script if run directly
    sample_data = scrape_reddit("Instagram", limit_per_sub=2)
    print(f"Sample data gathered: {len(sample_data)} records.")
