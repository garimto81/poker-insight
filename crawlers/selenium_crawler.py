#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 기반 크롤러 (Cloudflare 우회용)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SeleniumCrawler:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        options = Options()
        
        # 헤드리스 모드 (백그라운드 실행)
        options.add_argument('--headless')
        
        # 봇 탐지 우회 옵션들
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # User-Agent 설정
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # 봇 탐지 스크립트 제거
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            logger.info("Please install Chrome and ChromeDriver")
            raise
            
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            
    def crawl_pokerscout(self):
        """PokerScout 크롤링 (Selenium)"""
        try:
            self.setup_driver()
            url = 'https://www.pokerscout.com'
            
            logger.info(f"Accessing {url} with Selenium...")
            self.driver.get(url)
            
            # 페이지 로드 대기
            time.sleep(5)
            
            # Cloudflare 체크 대기
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ranktable"))
                )
            except:
                logger.warning("Waiting for page load...")
                time.sleep(10)
            
            # 테이블 찾기
            try:
                table = self.driver.find_element(By.CLASS_NAME, "ranktable")
                rows = table.find_elements(By.TAG_NAME, "tr")[1:11]  # 상위 10개
                
                logger.info(f"Found {len(rows)} poker sites")
                
                results = []
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 6:
                        data = {
                            'rank': cols[0].text.strip(),
                            'site': cols[1].text.strip(),
                            'cash_players': cols[2].text.strip(),
                            'tournament_players': cols[3].text.strip(),
                            'total_players': cols[4].text.strip(),
                            '7_day_avg': cols[5].text.strip()
                        }
                        results.append(data)
                        logger.info(f"{data['rank']}. {data['site']} - {data['total_players']} players")
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to parse table: {str(e)}")
                # 페이지 소스 저장 (디버깅용)
                with open('pokerscout_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info("Page source saved to pokerscout_page.html for debugging")
                
        except Exception as e:
            logger.error(f"Selenium crawl failed: {str(e)}")
        finally:
            self.close()
            
    def crawl_pokernews(self):
        """PokerNews 크롤링 (Selenium)"""
        try:
            self.setup_driver()
            url = 'https://www.pokernews.com/news/'
            
            logger.info(f"Accessing {url} with Selenium...")
            self.driver.get(url)
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # 뉴스 아이템 찾기
            news_items = []
            
            # 다양한 선택자 시도
            selectors = [
                "article",
                "[class*='news-item']",
                "[class*='article']",
                ".news-list li",
                ".content-item"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        break
                except:
                    continue
                    
            # 링크 기반 접근
            if not elements:
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/news/']")
                logger.info(f"Found {len(links)} news links")
                
                for link in links[:10]:
                    try:
                        title = link.text.strip()
                        if title and len(title) > 10:  # 의미있는 제목만
                            href = link.get_attribute('href')
                            news_items.append({
                                'title': title,
                                'url': href,
                                'date': datetime.now().isoformat()
                            })
                    except:
                        continue
                        
            logger.info(f"Collected {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Selenium crawl failed: {str(e)}")
        finally:
            self.close()

def test_selenium_crawler():
    """Selenium 크롤러 테스트"""
    logging.basicConfig(level=logging.INFO)
    
    crawler = SeleniumCrawler()
    
    # PokerScout 테스트
    print("\n=== Testing PokerScout with Selenium ===")
    scout_data = crawler.crawl_pokerscout()
    
    # PokerNews 테스트
    print("\n=== Testing PokerNews with Selenium ===")
    news_data = crawler.crawl_pokernews()
    
    print("\n=== Results ===")
    print(f"PokerScout: {'Success' if scout_data else 'Failed'}")
    print(f"PokerNews: {'Success' if news_data else 'Failed'}")

if __name__ == "__main__":
    test_selenium_crawler()