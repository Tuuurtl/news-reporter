import sqlite3
import re
import json
from datetime import datetime
import os

DB_PATH = '/news-data/news.db'
OUTPUT_JSON = '/opt/data/home/repos/news-reporter/news_structured.json'

def clean_sender(sender):
    if not sender:
        return "Unknown"
    return sender.split('<')[0].strip()

def to_title_case(text):
    # Convert ALL CAPS to title case, but keep some acronyms
    if text.isupper():
        return text.capitalize() # Simple version: just capitalize first letter
    return text

def parse_content(content):
    articles = []
    
    # 1. Extract all links from the bottom of the email
    links_map = {}
    links_section = re.split(r'Links:\s*\n------', content)
    if len(links_section) > 1:
        links_text = links_section[1]
        link_matches = re.findall(r'\[(\d+)\]\s*(https?://\S+)', links_text)
        for idx, url in link_matches:
            links_map[idx] = url

    # 2. Split content by categories or major sections
    # We use emoji or common section headers as split points
    sections = re.split(r'\n\s*([🚀💻🧠🎁⚡\s]+)\s*\n\s*([A-Z\s&]+)\n', content)
    
    # The first part of the split is usually the header/sponsor
    # We start processing from the first category found
    current_category = "General"
    
    # Improved regex for articles: 
    # Pattern: Title (Optional MIN READ) [LinkID] \n\n Description
    # Example: "BEFORE MASS LAYOFFS... (4 MINUTE READ) [5] \n\n Meta is moving..."
    article_pattern = re.compile(
        r'([A-Z\s\.:\?\!,\(\)\-]+?)\s*(?:\(\d+\s*(?:MINUTE|MIN)\s*READ\))?\s*\[(\d+)\]\s*\n+([^\n]+)', 
        re.MULTILINE
    )

    # Since re.split can be messy, we can also just iterate through the text 
    # but let's try to find all blocks that look like articles.
    
    # To handle sections correctly, we'll iterate through the parts
    for i in range(1, len(sections), 3):
        category_emoji = sections[i].strip()
        category_name = sections[i+1].strip()
        section_text = sections[i+2]
        
        matches = article_pattern.finditer(section_text)
        for match in matches:
            title = match.group(1).strip()
            link_id = match.group(2)
            desc = match.group(3).strip()
            
            # Filter out known noise
            if any(noise in title.lower() for noise in ["love tldr", "advertise", "work at tldr", "apply here", "referral"]):
                continue
            
            url = links_map.get(link_id, "#")
            
            articles.append({
                "title": to_title_case(title),
                "description": desc,
                "link": url,
                "section": category_name if category_name else "General"
            })

    return articles

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, sender, content, email_date FROM newsletters ORDER BY email_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    structured_data = []
    
    for row in rows:
        id, sender, content, date = row
        articles = parse_content(content)
        
        if not articles:
            continue
            
        structured_data.append({
            "id": id,
            "date": date,
            "sender": clean_sender(sender),
            "articles": articles
        })
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully processed {len(structured_data)} newsletters and saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
