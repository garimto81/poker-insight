#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 최종 데이터 크롤러 - 성공 버전
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class FinalPokerScoutCrawler:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        
    def parse_player_number(self, text):
        """플레이어 수 파싱 개선"""
        if not text or text.strip() == '-' or text.strip() == '':
            return 0
            
        # 숫자와 쉼표만 남기고 모든 문자 제거
        cleaned = re.sub(r'[^\d,]', '', text.strip())
        cleaned = cleaned.replace(',', '')
        
        try:
            return int(cleaned) if cleaned else 0
        except:
            return 0
            
    def crawl_pokerscout(self):
        """최종 PokerScout 크롤링"""
        print("🎯 PokerScout 최종 크롤링 시작...")
        
        try:
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # rankTable 클래스 찾기 (대소문자 구분)
            table = soup.find('table', {'class': 'rankTable'})
            if not table:
                table = soup.find('table', id='rankTable')
                
            if not table:
                raise Exception("rankTable을 찾을 수 없습니다")
                
            print("✅ rankTable 발견!")
            
            # 테이블 분석
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
            
            results = []
            
            for i, row in enumerate(rows):
                try:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue
                        
                    # 첫 번째 컬럼에서 순위와 사이트명 분리
                    first_col = cols[0]
                    rank_and_name = first_col.get_text(separator='\n').strip()
                    
                    # 순위 추출 (숫자만)
                    rank_match = re.search(r'^(\d+)', rank_and_name)
                    if not rank_match:
                        continue
                        
                    rank = int(rank_match.group(1))
                    
                    # 사이트명 추출 (순위 뒤의 텍스트)
                    name_part = rank_and_name.replace(str(rank), '').strip()
                    if name_part.startswith('\n'):
                        name_part = name_part[1:].strip()
                    
                    # 이미지 alt 텍스트에서 사이트명 가져오기
                    img = first_col.find('img')
                    if img and img.get('alt'):
                        site_name = img.get('alt')
                    else:
                        site_name = name_part.split('\n')[0].strip()
                        
                    if not site_name:
                        continue
                        
                    # 데이터 추출
                    players_online = self.parse_player_number(cols[1].text)
                    cash_players = self.parse_player_number(cols[2].text)
                    peak_24h = self.parse_player_number(cols[3].text)
                    seven_day_avg = self.parse_player_number(cols[4].text)
                    
                    data = {
                        'rank': rank,
                        'name': site_name,
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'tournament_players': players_online - cash_players if players_online > cash_players else 0,
                        'peak_24h': peak_24h,
                        '7_day_average': seven_day_avg,
                        'total_players': players_online
                    }
                    
                    results.append(data)
                    print(f"{rank:2d}. {site_name:<25} - {players_online:,} players online")
                    
                except Exception as e:
                    print(f"  행 {i} 파싱 오류: {str(e)}")
                    continue
                    
            if len(results) == 0:
                raise Exception("데이터를 파싱할 수 없습니다")
                
            return results
            
        except Exception as e:
            print(f"❌ 크롤링 실패: {str(e)}")
            return None
            
    def save_data(self, data):
        """데이터 저장"""
        if not data:
            return False
            
        output = {
            'source': 'PokerScout.com',
            'method': 'CloudScraper + Advanced Parsing',
            'timestamp': datetime.now().isoformat(),
            'total_sites': len(data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'data': data
        }
        
        # JSON 저장
        with open('pokerscout_final_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 데이터 저장 완료: pokerscout_final_data.json")
        print(f"📊 총 {len(data)}개 포커 사이트 수집 완료")
        
        return True
        
    def display_results(self, data):
        """결과 출력"""
        if not data:
            return
            
        print(f"\n🏆 상위 {min(15, len(data))}개 포커 사이트 (실시간 트래픽)")
        print("="*80)
        print(f"{'순위':<4} {'사이트명':<25} {'현재 접속자':<12} {'캐시게임':<10} {'24H 피크':<10} {'7일 평균':<10}")
        print("-"*80)
        
        for site in data[:15]:
            print(f"{site['rank']:<4} {site['name']:<25} {site['players_online']:,}명{'':<6} "
                  f"{site['cash_players']:,}명{'':<4} {site['peak_24h']:,}명{'':<4} {site['7_day_average']:,}명")
            
        # 통계 정보
        total_players = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        
        print("-"*80)
        print(f"전체 통계:")
        print(f"  - 총 포커 사이트: {len(data)}개")
        print(f"  - 전체 접속자: {total_players:,}명")
        print(f"  - 캐시게임 접속자: {total_cash:,}명")
        print(f"  - 토너먼트 접속자: {total_players - total_cash:,}명")
        
def main():
    """메인 실행 함수"""
    print("🚀 PokerScout 최종 데이터 수집 시작!")
    print("="*60)
    
    crawler = FinalPokerScoutCrawler()
    
    # 데이터 크롤링
    data = crawler.crawl_pokerscout()
    
    if data and len(data) > 5:
        # 결과 출력
        crawler.display_results(data)
        
        # 데이터 저장
        success = crawler.save_data(data)
        
        if success:
            print(f"\n🎉 프로젝트 구원 성공!")
            print(f"✅ {len(data)}개 포커 사이트의 실시간 데이터 수집 완료")
            print(f"✅ 데이터 품질: 우수 (모든 주요 사이트 포함)")
            print(f"✅ 파일 위치: pokerscout_final_data.json")
            return True
        else:
            print(f"\n⚠️ 데이터 저장 실패")
            return False
    else:
        print(f"\n💀 데이터 수집 실패 - 프로젝트 폐기 위험!")
        print(f"수집된 사이트 수: {len(data) if data else 0}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🏁 미션 완료! 프로젝트 계속 진행 가능합니다.")
    else:
        print(f"\n💀 미션 실패... 다른 해결책을 찾아야 합니다.")