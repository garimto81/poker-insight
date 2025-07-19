#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 워크플로우 자동 실행 및 로그 분석기
- GitHub API를 사용해 워크플로우 트리거
- 실시간 상태 모니터링
- 로그 자동 다운로드 및 분석
"""
import requests
import time
import json
import sys
import os
from datetime import datetime

class GitHubWorkflowRunner:
    def __init__(self, token=None):
        self.owner = "garimto81"
        self.repo = "poker-insight"
        self.workflow_file = "daily-data-collection.yml"
        
        # GitHub Personal Access Token (필요시 설정)
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Claude-Code-Workflow-Runner'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def trigger_workflow(self):
        """워크플로우 수동 실행 트리거"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/workflows/{self.workflow_file}/dispatches"
        
        data = {
            "ref": "main",
            "inputs": {
                "manual_run": "true"
            }
        }
        
        print("GitHub Actions 워크플로우 실행 중...")
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 204:
            print("[SUCCESS] 워크플로우 실행 요청 성공")
            return True
        else:
            print(f"[ERROR] 워크플로우 실행 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    
    def get_latest_run(self):
        """최신 워크플로우 실행 정보 조회"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            runs = response.json()['workflow_runs']
            if runs:
                return runs[0]  # 가장 최근 실행
        return None
    
    def get_run_jobs(self, run_id):
        """워크플로우 실행의 잡 목록 조회"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()['jobs']
        return []
    
    def download_logs(self, run_id):
        """워크플로우 로그 다운로드"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/logs"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            filename = f"workflow_logs_{run_id}.zip"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"[INFO] 로그 다운로드 완료: {filename}")
            return filename
        else:
            print(f"[ERROR] 로그 다운로드 실패: {response.status_code}")
            return None
    
    def monitor_workflow(self, timeout_minutes=10):
        """워크플로우 실행 모니터링"""
        print(f"[INFO] 워크플로우 모니터링 시작 (최대 {timeout_minutes}분)...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            latest_run = self.get_latest_run()
            
            if not latest_run:
                print("[ERROR] 워크플로우 실행을 찾을 수 없습니다")
                time.sleep(10)
                continue
            
            run_id = latest_run['id']
            status = latest_run['status']
            conclusion = latest_run['conclusion']
            
            print(f"[INFO] 실행 ID: {run_id}")
            print(f"[INFO] 상태: {status}")
            
            if status == 'completed':
                print(f"[RESULT] 완료 상태: {conclusion}")
                
                # 잡 상세 정보 출력
                jobs = self.get_run_jobs(run_id)
                for job in jobs:
                    job_status = "[SUCCESS]" if job['conclusion'] == 'success' else "[FAILED]"
                    print(f"  {job_status} {job['name']}: {job['conclusion']}")
                    
                    # 각 스텝 상태
                    for step in job['steps']:
                        step_status = "[OK]" if step['conclusion'] == 'success' else "[FAIL]"
                        print(f"    {step_status} {step['name']}")
                
                if conclusion == 'success':
                    print("[SUCCESS] 워크플로우 성공 완료!")
                    return True, run_id
                else:
                    print("[FAILED] 워크플로우 실패")
                    return False, run_id
            
            elif status in ['queued', 'in_progress']:
                print(f"[PROGRESS] 진행 중... ({int(time.time() - start_time)}초 경과)")
                time.sleep(10)
            else:
                print(f"[UNKNOWN] 알 수 없는 상태: {status}")
                time.sleep(10)
        
        print(f"[TIMEOUT] 타임아웃 ({timeout_minutes}분 초과)")
        return False, None
    
    def analyze_logs_summary(self, run_id):
        """로그 요약 분석 (API 기반)"""
        jobs = self.get_run_jobs(run_id)
        
        print("\n=== 워크플로우 실행 요약 ===")
        print("=" * 50)
        
        for job in jobs:
            print(f"\n[JOB] {job['name']}")
            print(f"   상태: {job['conclusion']}")
            print(f"   시작: {job['started_at']}")
            print(f"   완료: {job['completed_at']}")
            
            success_steps = sum(1 for step in job['steps'] if step['conclusion'] == 'success')
            total_steps = len(job['steps'])
            print(f"   단계: {success_steps}/{total_steps} 성공")
            
            # 실패한 단계 표시
            failed_steps = [step for step in job['steps'] if step['conclusion'] == 'failure']
            if failed_steps:
                print("   [FAILED STEPS]:")
                for step in failed_steps:
                    print(f"      - {step['name']}")
    
    def run_and_monitor(self):
        """워크플로우 실행 및 모니터링 전체 프로세스"""
        print("=== GG POKER 모니터링 시스템 - 자동 실행 ===")
        print("=" * 50)
        
        # 1. 워크플로우 트리거
        if not self.trigger_workflow():
            return False
        
        print("[INFO] 워크플로우 시작 대기 중...")
        time.sleep(5)  # GitHub에서 워크플로우가 시작될 때까지 잠시 대기
        
        # 2. 모니터링
        success, run_id = self.monitor_workflow()
        
        # 3. 결과 분석
        if run_id:
            self.analyze_logs_summary(run_id)
            
            if success:
                print("\n=== 대시보드 접속 정보 ===")
                print(f"메인 대시보드: https://{self.owner}.github.io/{self.repo}/")
                print(f"API 데이터: https://{self.owner}.github.io/{self.repo}/api_data.json")
        
        return success

def main():
    """메인 실행"""
    runner = GitHubWorkflowRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor-only":
        # 모니터링만 실행
        print("[INFO] 기존 워크플로우 모니터링...")
        success, run_id = runner.monitor_workflow()
        if run_id:
            runner.analyze_logs_summary(run_id)
    else:
        # 전체 실행
        success = runner.run_and_monitor()
        
        if success:
            print("\n[SUCCESS] 자동화 완료!")
            sys.exit(0)
        else:
            print("\n[FAILED] 자동화 실패")
            sys.exit(1)

if __name__ == "__main__":
    main()