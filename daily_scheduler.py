#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 사이트 일일 데이터 수집 스케줄러
- 매일 자동 데이터 수집
- 여러 시간대 수집으로 데이터 정확도 향상
- 에러 복구 및 재시도 로직
- 한 달간 무인 운영
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import schedule
import threading
from datetime import datetime, timedelta
import logging
from production_data_collector import ProductionDataCollector

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DailyScheduler:
    def __init__(self):
        self.collector = ProductionDataCollector()
        self.is_running = False
        self.collection_times = [
            "09:00",  # 오전 9시 (미국 야간)
            "15:00",  # 오후 3시 (유럽 오후)
            "21:00"   # 오후 9시 (아시아 저녁, 미국 오전)
        ]
        self.max_retries = 3
        self.retry_delay = 300  # 5분
        
    def setup_schedule(self):
        """수집 스케줄 설정"""
        logger.info("📅 일일 데이터 수집 스케줄 설정...")
        
        for collection_time in self.collection_times:
            schedule.every().day.at(collection_time).do(self.scheduled_collection)
            logger.info(f"  ⏰ {collection_time} - 데이터 수집 예약됨")
        
        # 주간 요약 리포트 (일요일 오전 10시)
        schedule.every().sunday.at("10:00").do(self.weekly_summary_report)
        
        # 시스템 상태 점검 (매일 자정)
        schedule.every().day.at("00:00").do(self.system_health_check)
        
        logger.info("✅ 스케줄 설정 완료")
        
    def scheduled_collection(self):
        """스케줄된 데이터 수집"""
        current_time = datetime.now().strftime('%H:%M')
        logger.info(f"🔄 스케줄된 데이터 수집 시작 ({current_time})")
        
        success = False
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"📡 데이터 수집 시도 {attempt}/{self.max_retries}")
                success = self.collector.run_daily_collection()
                
                if success:
                    logger.info(f"✅ 데이터 수집 성공 (시도 {attempt})")
                    break
                else:
                    logger.warning(f"⚠️ 데이터 수집 실패 (시도 {attempt})")
                    
            except Exception as e:
                logger.error(f"❌ 데이터 수집 오류 (시도 {attempt}): {str(e)}")
            
            # 재시도 전 대기
            if attempt < self.max_retries:
                logger.info(f"⏳ {self.retry_delay}초 후 재시도...")
                time.sleep(self.retry_delay)
        
        if not success:
            logger.error(f"💀 모든 재시도 실패 - 수동 점검 필요")
            self.send_failure_alert()
        
        return success
    
    def send_failure_alert(self):
        """수집 실패 알림 (로그 기반)"""
        alert_message = f"""
        🚨 포커 데이터 수집 실패 알림
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        상태: 모든 재시도 실패
        조치: 수동 점검 필요
        로그: scheduler.log 확인
        """
        
        logger.critical(alert_message)
        
        # 실제 환경에서는 이메일, 슬랙 등으로 알림 발송
        # 여기서는 로그에만 기록
        
    def weekly_summary_report(self):
        """주간 요약 리포트 생성"""
        logger.info("📊 주간 요약 리포트 생성...")
        
        try:
            summary = self.collector.get_collection_summary(7)
            
            report = f"""
            📈 주간 포커 데이터 수집 요약 리포트
            =============================================
            수집 기간: {summary['collection_period']['first_date']} ~ {summary['collection_period']['last_date']}
            총 수집 일수: {summary['collection_period']['total_days']}일
            일평균 사이트: {summary['averages']['sites_per_day']}개
            일평균 플레이어: {summary['averages']['players_per_day']:,.0f}명
            
            📅 최근 수집 내역:
            """
            
            for collection in summary['recent_collections'][:7]:
                report += f"  {collection['date']}: {collection['sites']}개 사이트, {collection['total_players']:,}명\n"
            
            logger.info(report)
            
            # 리포트 파일 저장
            timestamp = datetime.now().strftime('%Y%m%d')
            with open(f'weekly_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
                f.write(report)
                
        except Exception as e:
            logger.error(f"❌ 주간 리포트 생성 실패: {str(e)}")
    
    def system_health_check(self):
        """시스템 상태 점검"""
        logger.info("🔍 시스템 상태 점검...")
        
        try:
            # 데이터베이스 연결 확인
            summary = self.collector.get_collection_summary(1)
            
            # 최근 수집 확인
            if summary['recent_collections']:
                last_collection = summary['recent_collections'][0]
                last_date = datetime.strptime(last_collection['date'], '%Y-%m-%d')
                days_since = (datetime.now() - last_date).days
                
                if days_since > 1:
                    logger.warning(f"⚠️ 마지막 수집: {days_since}일 전")
                else:
                    logger.info(f"✅ 시스템 정상 (마지막 수집: {last_collection['date']})")
            else:
                logger.warning("⚠️ 수집 기록이 없습니다")
                
            # 디스크 공간 확인
            self.check_disk_space()
            
        except Exception as e:
            logger.error(f"❌ 시스템 상태 점검 실패: {str(e)}")
    
    def check_disk_space(self):
        """디스크 공간 확인"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free / (1024**3)
            
            if free_gb < 1.0:  # 1GB 미만
                logger.warning(f"⚠️ 디스크 공간 부족: {free_gb:.1f}GB")
            else:
                logger.info(f"💽 디스크 공간: {free_gb:.1f}GB 여유")
                
        except Exception as e:
            logger.error(f"❌ 디스크 공간 확인 실패: {str(e)}")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        self.is_running = True
        logger.info("🚀 포커 데이터 수집 스케줄러 시작")
        logger.info(f"📅 수집 시간: {', '.join(self.collection_times)}")
        logger.info("🔄 무한 실행 모드 (Ctrl+C로 중지)")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
                
        except KeyboardInterrupt:
            logger.info("⏹️ 사용자에 의해 중지됨")
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {str(e)}")
        finally:
            self.is_running = False
            logger.info("🔚 스케줄러 종료")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        
    def manual_collection(self):
        """수동 데이터 수집"""
        logger.info("🔧 수동 데이터 수집 실행...")
        success = self.collector.run_daily_collection()
        return success
    
    def get_next_scheduled_time(self):
        """다음 예약된 수집 시간"""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run
        return None

class SchedulerManager:
    """스케줄러 관리 클래스"""
    
    def __init__(self):
        self.scheduler = DailyScheduler()
        
    def start_30_day_collection(self):
        """30일간 데이터 수집 시작"""
        print("🎯 30일간 포커 데이터 자동 수집 시작")
        print("=" * 50)
        
        # 즉시 한 번 수집
        print("📡 초기 데이터 수집...")
        initial_success = self.scheduler.manual_collection()
        
        if initial_success:
            print("✅ 초기 수집 완료")
        else:
            print("❌ 초기 수집 실패 - 그래도 스케줄러 시작")
        
        # 스케줄 설정
        self.scheduler.setup_schedule()
        
        # 다음 수집 시간 안내
        next_time = self.scheduler.get_next_scheduled_time()
        if next_time:
            print(f"⏰ 다음 수집 예정: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n🔄 자동 수집 시작 - 30일간 무인 운영")
        print("📋 로그 파일: scheduler.log")
        print("🛑 중지: Ctrl+C")
        print("-" * 50)
        
        # 스케줄러 실행
        self.scheduler.run_scheduler()
    
    def status_check(self):
        """수집 상태 확인"""
        print("📊 포커 데이터 수집 현황")
        print("=" * 40)
        
        try:
            summary = self.scheduler.collector.get_collection_summary(7)
            
            print(f"총 수집 일수: {summary['collection_period']['total_days']}일")
            print(f"수집 기간: {summary['collection_period']['first_date']} ~ {summary['collection_period']['last_date']}")
            print(f"일평균 사이트: {summary['averages']['sites_per_day']}개")
            print(f"일평균 플레이어: {summary['averages']['players_per_day']:,.0f}명")
            
            if summary['recent_collections']:
                print(f"\n📅 최근 수집 내역:")
                for collection in summary['recent_collections'][:5]:
                    gg_sites = collection['gg_poker_sites']
                    print(f"  {collection['date']}: {collection['sites']}개 사이트 (GG: {gg_sites}), {collection['total_players']:,}명")
            
            print(f"\n✅ 수집 시스템 정상 가동 중")
            
        except Exception as e:
            print(f"❌ 상태 확인 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='포커 데이터 수집 스케줄러')
    parser.add_argument('--start', action='store_true', help='30일간 자동 수집 시작')
    parser.add_argument('--status', action='store_true', help='수집 현황 확인') 
    parser.add_argument('--manual', action='store_true', help='수동 수집 실행')
    
    args = parser.parse_args()
    
    manager = SchedulerManager()
    
    if args.start:
        manager.start_30_day_collection()
    elif args.status:
        manager.status_check()
    elif args.manual:
        print("🔧 수동 데이터 수집...")
        success = manager.scheduler.manual_collection()
        if success:
            print("✅ 수동 수집 완료")
        else:
            print("❌ 수동 수집 실패")
    else:
        print("🎯 포커 데이터 수집 스케줄러")
        print("사용법:")
        print("  --start   : 30일간 자동 수집 시작")
        print("  --status  : 수집 현황 확인")
        print("  --manual  : 수동 수집 실행")

if __name__ == "__main__":
    main()