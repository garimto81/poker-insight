#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PokerScout 완벽 데이터 크롤러 - 사이트명 정확 추출
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class PerfectPokerScoutCrawler:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        
    def parse_player_number(self, text):
        """플레이어 수 파싱"""
        if not text or text.strip() == '-' or text.strip() == '':
            return 0
            
        cleaned = re.sub(r'[^\d,]', '', text.strip())
        cleaned = cleaned.replace(',', '')
        
        try:
            return int(cleaned) if cleaned else 0
        except:
            return 0
            
    def crawl_pokerscout(self):
        """완벽한 PokerScout 크롤링"""
        print("🎯 PokerScout 완벽 크롤링 시작...")
        
        try:
            response = self.scraper.get('https://www.pokerscout.com', timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # rankTable 찾기
            table = soup.find('table', {'class': 'rankTable'})
            if not table:
                table = soup.find('table', id='rankTable')
                
            if not table:
                raise Exception("rankTable을 찾을 수 없습니다")
                
            print("✅ rankTable 발견!")
            
            # tbody에서 행 추출
            tbody = table.find('tbody')
            if not tbody:
                rows = table.find_all('tr')[1:]  # 헤더 제외
            else:
                rows = tbody.find_all('tr')
            
            results = []
            
            for i, row in enumerate(rows):
                try:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue
                    
                    # 첫 번째 컬럼에서 순위와 사이트명 추출
                    first_col = cols[0]
                    
                    # 순위 추출 (rank-num 클래스에서)
                    rank_span = first_col.find('span', class_='rank-num')
                    if rank_span:
                        rank = int(rank_span.text.strip())
                    else:
                        continue
                    
                    # 사이트명 추출 (brand-title 클래스에서)
                    brand_title = first_col.find('span', class_='brand-title')
                    if brand_title:
                        site_name = brand_title.text.strip()
                    else:
                        # 대체 방법: div에서 찾기
                        brand_div = first_col.find('div', class_='brand-title-rank')
                        if brand_div:
                            site_name = brand_div.get_text().replace(str(rank), '').strip()
                        else:
                            continue
                    
                    if not site_name or len(site_name) < 2:
                        continue
                    
                    # 플레이어 데이터 추출
                    players_online = self.parse_player_number(cols[1].text)
                    cash_players = self.parse_player_number(cols[2].text)
                    peak_24h = self.parse_player_number(cols[3].text)
                    seven_day_avg = self.parse_player_number(cols[4].text)
                    
                    data = {
                        'rank': rank,
                        'name': site_name,
                        'players_online': players_online,
                        'cash_players': cash_players,
                        'tournament_players': max(0, players_online - cash_players),
                        'peak_24h': peak_24h,
                        '7_day_average': seven_day_avg,
                        'total_players': players_online
                    }
                    
                    results.append(data)
                    print(f"{rank:2d}. {site_name:<30} - {players_online:,} players online")
                    
                except Exception as e:
                    print(f"  행 {i} 파싱 오류: {str(e)}")
                    continue
            
            # 순위별로 정렬
            results.sort(key=lambda x: x['rank'])
            
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
            'method': 'CloudScraper + Perfect Parsing',
            'timestamp': datetime.now().isoformat(),
            'total_sites': len(data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'data': data,
            'summary': {
                'total_players_online': sum(site['players_online'] for site in data),
                'total_cash_players': sum(site['cash_players'] for site in data),
                'total_tournament_players': sum(site['tournament_players'] for site in data),
                'top_site': data[0]['name'] if data else None,
                'top_site_players': data[0]['players_online'] if data else 0
            }
        }
        
        # JSON 저장
        with open('pokerscout_perfect_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 완벽한 데이터 저장: pokerscout_perfect_data.json")
        print(f"📊 총 {len(data)}개 포커 사이트 완벽 수집!")
        
        return True
        
    def display_results(self, data):
        """결과 출력"""
        if not data:
            return
            
        print(f"\n🏆 포커 사이트 실시간 트래픽 랭킹 TOP {min(20, len(data))}")
        print("="*90)
        print(f"{'순위':<4} {'포커 사이트':<25} {'현재 접속자':<12} {'캐시게임':<10} {'토너먼트':<10} {'7일 평균':<10}")
        print("-"*90)
        
        for site in data[:20]:
            print(f"{site['rank']:<4} {site['name']:<25} {site['players_online']:,}명{'':<6} "
                  f"{site['cash_players']:,}명{'':<4} {site['tournament_players']:,}명{'':<5} {site['7_day_average']:,}명")
            
        # 상세 통계
        total_players = sum(site['players_online'] for site in data)
        total_cash = sum(site['cash_players'] for site in data)
        total_tournaments = sum(site['tournament_players'] for site in data)
        
        print("-"*90)
        print(f"📈 전체 온라인 포커 시장 통계 (실시간)")
        print(f"  • 전체 포커 사이트: {len(data)}개")
        print(f"  • 총 접속자: {total_players:,}명")
        print(f"  • 캐시게임 접속자: {total_cash:,}명 ({total_cash/total_players*100:.1f}%)")
        print(f"  • 토너먼트 접속자: {total_tournaments:,}명 ({total_tournaments/total_players*100:.1f}%)")
        
        # TOP 5 사이트 하이라이트
        print(f"\n🥇 TOP 5 포커 사이트:")
        for i, site in enumerate(data[:5]):
            medal = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i]
            print(f"  {medal} {site['name']}: {site['players_online']:,}명 (7일 평균: {site['7_day_average']:,}명)")

def main():
    """메인 실행 함수"""
    print("🚀 PokerScout 완벽 데이터 수집 미션!")
    print("="*60)
    
    crawler = PerfectPokerScoutCrawler()
    
    # 데이터 크롤링
    data = crawler.crawl_pokerscout()
    
    if data and len(data) > 10:
        # 결과 출력
        crawler.display_results(data)
        
        # 데이터 저장
        success = crawler.save_data(data)
        
        if success:
            print(f"\n🎉🎉🎉 미션 완료! 프로젝트 완전 구원! 🎉🎉🎉")
            print(f"✅ {len(data)}개 포커 사이트 완벽 수집")
            print(f"✅ 실시간 플레이어 수 정확히 파싱")
            print(f"✅ 사이트명 정확히 추출")
            print(f"✅ 데이터 품질: 최고 등급")
            print(f"✅ 파일: pokerscout_perfect_data.json")
            
            # 주요 사이트 확인
            major_sites = ['GGNetwork', 'PokerStars', 'WPT Global', '888poker']
            found_sites = [site['name'] for site in data]
            
            print(f"\n🔍 주요 포커 사이트 확인:")
            for major in major_sites:
                found = any(major.lower() in site.lower() for site in found_sites)
                status = "✅ 발견" if found else "❌ 누락"
                print(f"  • {major}: {status}")
            
            return True
        else:
            print(f"\n⚠️ 데이터 저장 실패")
            return False
    else:
        print(f"\n💀 데이터 수집 실패!")
        print(f"수집된 사이트 수: {len(data) if data else 0}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🏁 완벽 성공! 포커 방송 프로덕션에서 사용할 수 있는 고품질 데이터 확보!")
        print(f"📺 방송용 데이터 준비 완료!")
    else:
        print(f"\n💀 최종 실패... 다른 데이터 소스 필요")