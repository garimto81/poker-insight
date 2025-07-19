#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수집 결과 알림 발송
- Discord Webhook 알림
- 수집 성공/실패 상태 전송
- 주요 통계 포함
"""
import os
import sys
import json
import requests
import argparse
from datetime import datetime
import glob

class NotificationSender:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK', '')
        
    def send_discord_notification(self, status, report_data=None):
        """Discord 알림 발송"""
        if not self.discord_webhook:
            print("⚠️ Discord webhook URL이 설정되지 않았습니다")
            return False
        
        try:
            now = datetime.now()
            
            if status == 'success':
                embed = {
                    "title": "✅ 포커 데이터 수집 성공",
                    "color": 3066993,  # 초록색
                    "timestamp": now.isoformat(),
                    "fields": []
                }
                
                if report_data:
                    embed["fields"] = [
                        {
                            "name": "📊 수집 통계",
                            "value": f"총 사이트: {report_data.get('total_sites', 0)}개\nGG POKER: {report_data.get('gg_poker_sites', 0)}개",
                            "inline": True
                        },
                        {
                            "name": "👥 플레이어 현황",
                            "value": f"총 플레이어: {report_data.get('total_players', 0):,}명\n캐시 플레이어: {report_data.get('total_cash_players', 0):,}명",
                            "inline": True
                        },
                        {
                            "name": "⏱️ 수집 시간",
                            "value": f"{report_data.get('duration_seconds', 0):.1f}초",
                            "inline": True
                        }
                    ]
                    
                    # GG POKER 데이터 하이라이트
                    gg_sites = [site for site in report_data.get('sites_data', []) if 'GG' in site['site_name']]
                    if gg_sites:
                        gg_info = "\n".join([f"• {site['site_name']}: {site['players_online']:,}명" for site in gg_sites])
                        embed["fields"].append({
                            "name": "🎯 GG POKER 현황",
                            "value": gg_info,
                            "inline": False
                        })
                
            else:  # failure
                embed = {
                    "title": "❌ 포커 데이터 수집 실패",
                    "color": 15158332,  # 빨간색
                    "timestamp": now.isoformat(),
                    "fields": [
                        {
                            "name": "🔍 확인 필요",
                            "value": "로그를 확인하여 문제를 해결해주세요.",
                            "inline": False
                        }
                    ]
                }
            
            payload = {
                "username": "Poker Data Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3514/3514491.png",
                "embeds": [embed]
            }
            
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            print(f"✅ Discord 알림 발송 완료 ({status})")
            return True
            
        except Exception as e:
            print(f"❌ Discord 알림 실패: {str(e)}")
            return False
    
    def get_latest_report(self):
        """최신 수집 리포트 로드"""
        try:
            report_files = glob.glob("collection_report_*.json")
            if not report_files:
                return None
            
            latest_file = max(report_files)
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ 리포트 로드 실패: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description='수집 알림 발송')
    parser.add_argument('--status', choices=['success', 'failure'], required=True, help='수집 상태')
    
    args = parser.parse_args()
    
    sender = NotificationSender()
    
    # 최신 리포트 데이터 가져오기
    report_data = None
    if args.status == 'success':
        report_data = sender.get_latest_report()
    
    # Discord 알림 발송
    success = sender.send_discord_notification(args.status, report_data)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()