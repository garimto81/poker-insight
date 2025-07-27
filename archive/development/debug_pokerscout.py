#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout HTML 구조 분석 및 디버깅
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime

def analyze_pokerscout_structure():
    """PokerScout 페이지 구조 분석"""
    print("🔍 PokerScout 페이지 구조 분석 중...")
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get('https://www.pokerscout.com', timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 접속 성공! 응답 크기: {len(response.content)} bytes")
            
            # HTML 파일로 저장
            with open('pokerscout_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("📄 HTML 파일 저장: pokerscout_page.html")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. 모든 테이블 찾기
            print("\n1. 테이블 구조 분석:")
            tables = soup.find_all('table')
            print(f"   총 {len(tables)}개 테이블 발견")
            
            for i, table in enumerate(tables):
                print(f"\n   테이블 {i+1}:")
                print(f"   - 클래스: {table.get('class', '없음')}")
                print(f"   - ID: {table.get('id', '없음')}")
                rows = table.find_all('tr')
                print(f"   - 행 수: {len(rows)}")
                
                if rows:
                    first_row = rows[0]
                    cols = first_row.find_all(['th', 'td'])
                    print(f"   - 첫 행 컬럼 수: {len(cols)}")
                    if cols:
                        headers = [col.text.strip() for col in cols]
                        print(f"   - 헤더: {headers}")
            
            # 2. ranktable 클래스 확인
            print("\n2. ranktable 클래스 확인:")
            ranktable = soup.find('table', {'class': 'ranktable'})
            if ranktable:
                print("   ✅ ranktable 발견!")
                analyze_ranktable(ranktable)
            else:
                print("   ❌ ranktable 없음")
                
            # 3. 다른 가능한 선택자들 확인
            print("\n3. 다른 가능한 선택자들:")
            selectors = [
                ('table[id*="rank"]', 'ID에 rank 포함'),
                ('table[class*="rank"]', '클래스에 rank 포함'),
                ('.rankings', '랭킹 클래스'),
                ('#rankings', '랭킹 ID'),
                ('div.poker-sites', '포커 사이트 div'),
                ('.site-list', '사이트 목록'),
                ('tbody tr', '테이블 바디 행들')
            ]
            
            for selector, desc in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   ✅ {desc}: {len(elements)}개 요소")
                    if selector == 'tbody tr' and len(elements) > 5:
                        print("      tbody tr 분석 시도...")
                        analyze_tbody_rows(elements)
                else:
                    print(f"   ❌ {desc}: 없음")
                    
            # 4. 텍스트에서 포커 사이트명 찾기
            print("\n4. 알려진 포커 사이트명 검색:")
            poker_sites = ['PokerStars', 'GGPoker', '888poker', 'partypoker', 'WPT', 'Americas Cardroom']
            page_text = soup.get_text()
            
            for site in poker_sites:
                if site.lower() in page_text.lower():
                    print(f"   ✅ {site} 발견")
                else:
                    print(f"   ❌ {site} 없음")
                    
        else:
            print(f"❌ 접속 실패: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def analyze_ranktable(table):
    """ranktable 상세 분석"""
    print("   ranktable 상세 분석:")
    rows = table.find_all('tr')
    
    for i, row in enumerate(rows[:5]):  # 상위 5개 행만
        cols = row.find_all(['th', 'td'])
        print(f"   행 {i+1}: {len(cols)}개 컬럼")
        for j, col in enumerate(cols):
            text = col.text.strip()
            print(f"     컬럼 {j+1}: '{text}'")

def analyze_tbody_rows(rows):
    """tbody 행들 분석"""
    print("   tbody 행 분석:")
    for i, row in enumerate(rows[:3]):  # 상위 3개만
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 4:
            texts = [col.text.strip() for col in cols]
            print(f"   행 {i+1}: {texts}")

def extract_real_data():
    """실제 데이터 추출 시도"""
    print("\n🎯 실제 데이터 추출 시도...")
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get('https://www.pokerscout.com', timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 방법 1: ranktable 다시 시도
            table = soup.find('table', {'class': 'ranktable'})
            if table:
                results = extract_from_ranktable(table)
                if results:
                    return results
                    
            # 방법 2: tbody 행들에서 추출
            tbody_rows = soup.select('tbody tr')
            if tbody_rows:
                results = extract_from_tbody(tbody_rows)
                if results:
                    return results
                    
            # 방법 3: 모든 테이블에서 포커 데이터 찾기
            tables = soup.find_all('table')
            for table in tables:
                results = extract_from_any_table(table)
                if results:
                    return results
                    
    except Exception as e:
        print(f"❌ 추출 오류: {str(e)}")
        
    return None

def extract_from_ranktable(table):
    """ranktable에서 데이터 추출"""
    results = []
    rows = table.find_all('tr')
    
    for row in rows[1:]:  # 헤더 스킵
        cols = row.find_all('td')
        if len(cols) >= 5:
            try:
                rank_text = cols[0].text.strip()
                name_text = cols[1].text.strip()
                
                # 숫자가 있는 행만 처리
                if rank_text.isdigit() and name_text and len(name_text) > 2:
                    data = {
                        'rank': int(rank_text),
                        'name': name_text,
                        'cash_players': parse_players(cols[2].text.strip()),
                        'tournament_players': parse_players(cols[3].text.strip()),
                        'total_players': parse_players(cols[4].text.strip()),
                        '7_day_average': parse_players(cols[5].text.strip()) if len(cols) > 5 else 0
                    }
                    results.append(data)
                    
            except:
                continue
                
    return results if len(results) > 5 else None

def extract_from_tbody(rows):
    """tbody 행에서 데이터 추출"""
    results = []
    
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) >= 4:
            try:
                # 포커 사이트명 패턴 찾기
                name_col = None
                for col in cols:
                    text = col.text.strip()
                    if any(word in text.lower() for word in ['poker', 'gg', '888', 'party', 'stars']):
                        name_col = text
                        break
                        
                if name_col:
                    data = {
                        'rank': i + 1,
                        'name': name_col,
                        'total_players': parse_players(cols[-1].text.strip())
                    }
                    results.append(data)
                    
            except:
                continue
                
    return results if len(results) > 3 else None

def extract_from_any_table(table):
    """모든 테이블에서 포커 데이터 찾기"""
    rows = table.find_all('tr')
    if len(rows) < 3:  # 최소 3행 필요
        return None
        
    results = []
    
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            for col in cols:
                text = col.text.strip()
                # 포커 사이트명 패턴
                if any(site in text for site in ['PokerStars', 'GGPoker', '888poker', 'partypoker']):
                    # 같은 행에서 숫자 찾기
                    numbers = []
                    for c in cols:
                        num = parse_players(c.text.strip())
                        if num > 0:
                            numbers.append(num)
                            
                    if numbers:
                        data = {
                            'rank': len(results) + 1,
                            'name': text,
                            'total_players': max(numbers)
                        }
                        results.append(data)
                        
    return results if len(results) > 2 else None

def parse_players(text):
    """플레이어 수 파싱"""
    if not text or text == '-':
        return 0
    text = text.replace(',', '').replace(' ', '').replace('players', '')
    try:
        return int(float(text))
    except:
        return 0

if __name__ == "__main__":
    # 1. 페이지 구조 분석
    analyze_pokerscout_structure()
    
    # 2. 실제 데이터 추출
    real_data = extract_real_data()
    
    if real_data:
        print(f"\n🎉 실제 데이터 추출 성공! {len(real_data)}개 사이트")
        
        output = {
            'source': 'PokerScout.com',
            'method': 'Advanced Parsing',
            'timestamp': datetime.now().isoformat(),
            'total_sites': len(real_data),
            'data': real_data
        }
        
        with open('pokerscout_fixed_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print("💾 수정된 데이터 저장: pokerscout_fixed_data.json")
        
        for site in real_data[:10]:
            print(f"{site['rank']}. {site['name']} - {site.get('total_players', 0):,} players")
            
    else:
        print("\n❌ 데이터 추출 실패")
        print("🔍 pokerscout_page.html 파일을 수동으로 확인해보세요.")