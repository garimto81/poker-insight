#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 크롤링 디버깅 - 새로운 HTML 구조 분석
"""
import cloudscraper
from bs4 import BeautifulSoup
import re

def debug_pokerscout():
    """PokerScout 크롤링 디버깅"""
    print("PokerScout crawling debug started...")
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'linux', 'mobile': False}
    )
    
    try:
        response = scraper.get('https://www.pokerscout.com', timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'rankTable'})
        
        if not table:
            print("ERROR: rankTable not found")
            return
        
        print("SUCCESS: Table found, analyzing new HTML structure...")
        
        rows = table.find_all('tr')[1:]  # Skip header
        print(f"FOUND: {len(rows)} rows total")
        
        valid_sites = 0
        
        for i, row in enumerate(rows[:10]):  # Check first 10 rows
            try:
                print(f"\\n=== ROW {i+1} DETAILED ANALYSIS ===")
                
                # Look for site name in img alt attribute
                img_tags = row.find_all('img')
                for img in img_tags:
                    alt_text = img.get('alt', '')
                    if alt_text and alt_text != 'Logo':
                        print(f"IMG ALT: '{alt_text}'")
                
                # Look for text in various elements
                all_texts = []
                for element in row.find_all(['span', 'div', 'td']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 1 and not text.isdigit():
                        all_texts.append(text)
                
                print(f"ALL TEXTS: {all_texts[:5]}")  # First 5 texts
                
                # Try to find numbers (player counts)
                numbers = []
                for element in row.find_all(['span', 'div', 'td']):
                    text = element.get_text(strip=True).replace(',', '')
                    if text.isdigit() and int(text) > 0:
                        numbers.append(int(text))
                
                print(f"NUMBERS FOUND: {numbers[:5]}")  # First 5 numbers
                
                # Show raw HTML for first few rows
                if i < 3:
                    print("RAW HTML:")
                    print(str(row)[:300] + "...")
                
            except Exception as e:
                print(f"ERROR parsing row {i+1}: {str(e)}")
        
        # Try alternative approach - look for specific patterns
        print("\\n=== ALTERNATIVE SEARCH ===")
        
        # Look for any elements with specific classes that might contain site names
        brand_elements = soup.find_all(['div', 'span'], class_=re.compile(r'brand|name|title'))
        print(f"Found {len(brand_elements)} brand-related elements")
        
        for i, element in enumerate(brand_elements[:10]):
            text = element.get_text(strip=True)
            if text and len(text) > 2:
                print(f"Brand element {i+1}: '{text}'")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    debug_pokerscout()