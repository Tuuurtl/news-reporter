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
    # Convert ALL CAPS to title case
    if text.isupper():
        return text.capitalize()
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

    # 2. Split content by categories
    sections = re.split(r'\n\s*([🚀💻🧠🎁⚡\s]+)\s*\n\s*([A-Z\s&]+)\n', content)
    
    # Robust article pattern
    # The title is typically the first line.
    # We look for the pattern: TITLE (X MIN READ) [ID] or TITLE (SPONSOR) [ID]
    article_pattern = re.compile(
        r'^([^\n]+?)\s*' # Title
        r'(?:\(\d+\s*(?:MINUTE|MIN)\s*READ\)|(?:\(SPONSOR\)))\s*' # Marker
        r'\[(\d+)\]\s*$', # Link ID
        re.MULTILINE | re.IGNORECASE
    )

    if len(sections) < 3:
        processing_units = [("General", content)]
    else:
        processing_units = []
        for i in range(1, len(sections), 3):
            category_name = sections[i+1].strip()
            section_text = sections[i+2]
            processing_units.append((category_name, section_text))

    for category_name, section_text in processing_units:
        matches = list(article_pattern.finditer(section_text))
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            link_id = match.group(2)
            
            # Description starts AFTER the line with the title/link
            start_idx = match.end() + 1 
            
            # Description ends at the start of the next match or the end of the section
            if i + 1 < len(matches):
                end_idx = matches[i+1].start()
            else:
                end_idx = len(section_text)
                
            desc = section_text[start_idx:end_idx].strip()
            
            # IMPORTANT: Clean up description if it contains subsequent articles 
            # (happens if the regex missed some articles but captured them in description)
            # Since the regex is now strict on " ( la min read) [id]", we should use that 
            # to trim descriptions further if they are too long or contain markers.
            
            # Remove trailing noise from the end of a section
            noise_markers = ["Love TLDR?", "Want to advertise", "Want to work at TLDR?"]
            for marker in noise_markers:
                if marker in desc:
                    desc = desc.split(marker)[0].strip()

            # Filtering noise in titles
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
        db_id, sender, content, date_str = row
        articles = parse_content(content)
        
        if not articles:
            continue
            
        # FIX: Truncate ISO date to YYYY-MM-DD
        formatted_date = date_str[:10] if date_str else "Unknown Date"
        
        structured_data.append({
            "id": db_id,
            "date": formatted_date,
            "sender": clean_sender(sender),
            "articles": articles
        })
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully processed {len(structured_data)} newsletters and saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
