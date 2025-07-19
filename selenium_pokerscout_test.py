#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 실제 데이터 크롤링 테스트 (Selenium 필요)
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

def crawl_real_pokerscout():
    print("=== PokerScout 실제 데이터 크롤링 시도 ===")
    print("\n필요사항:")
    print("1. Chrome 브라우저 설치")
    print("2. ChromeDriver 다운로드 및 PATH 설정")
    print("   다운로드: https://chromedriver.chromium.org/")
    
    try:
        # Chrome 옵션 설정
        options = Options()
        # 헤드리스 모드 비활성화 (실제 브라우저 창 표시)
        # options.add_argument('--headless')
        
        # 봇 탐지 우회
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("\nChrome 드라이버 시작 중...")
        driver = webdriver.Chrome(options=options)
        
        # 봇 탐지 스크립트 제거
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("PokerScout.com 접속 중...")
        driver.get('https://www.pokerscout.com')
        
        print("Cloudflare 체크 통과 대기 중... (최대 30초)")
        print("브라우저 창에서 'Checking your browser' 메시지가 사라질 때까지 기다려주세요.")
        
        # Cloudflare 통과 대기
        time.sleep(10)
        
        try:
            # 테이블 대기
            table = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ranktable"))
            )
            print("\n✓ 랭킹 테이블 발견!")
            
            # 데이터 추출
            rows = driver.find_elements(By.CSS_SELECTOR, ".ranktable tr")[1:]  # 헤더 제외
            
            real_data = []
            print(f"\n총 {len(rows)}개 사이트 발견. 상위 10개 표시:")
            
            for i, row in enumerate(rows[:10]):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    data = {
                        'rank': cols[0].text.strip(),
                        'name': cols[1].text.strip(),
                        'cash_players': cols[2].text.strip(),
                        'tournament_players': cols[3].text.strip(),
                        'total_players': cols[4].text.strip(),
                        '7_day_average': cols[5].text.strip()
                    }
                    real_data.append(data)
                    print(f"{data['rank']}. {data['name']} - {data['total_players']} players (7일 평균: {data['7_day_average']})")
            
            # 실제 데이터 저장
            if real_data:
                output = {
                    'source': 'PokerScout.com',
                    'timestamp': datetime.now().isoformat(),
                    'data': real_data
                }
                
                with open('pokerscout_real_data.json', 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                
                print(f"\n✓ 실제 데이터가 'pokerscout_real_data.json'에 저장되었습니다.")
                print(f"✓ 총 {len(real_data)}개 사이트 데이터 수집 완료")
            
        except Exception as e:
            print(f"\n✗ 테이블을 찾을 수 없습니다: {str(e)}")
            print("\n페이지 소스 일부:")
            print(driver.page_source[:500])
            
    except Exception as e:
        print(f"\n✗ ChromeDriver 오류: {str(e)}")
        print("\n해결 방법:")
        print("1. pip install selenium")
        print("2. Chrome 브라우저 설치")
        print("3. ChromeDriver 다운로드 후 PATH에 추가")
        print("   또는 python -m selenium install 실행")
        
    finally:
        if 'driver' in locals():
            input("\n엔터 키를 누르면 브라우저가 종료됩니다...")
            driver.quit()

if __name__ == "__main__":
    crawl_real_pokerscout()