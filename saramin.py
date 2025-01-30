import os
import json
import time
import smtplib
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ✅ JSON에서 lastNo 불러오기
def get_lastNo_from_json():
    try:
        with open('latest.json', 'r') as json_file:
            data = json.load(json_file)
            return data.get("lastNo", 0)
    except FileNotFoundError:
        return 0  # 파일이 없으면 기본값 0

# ✅ JSON에 lastNo 업데이트
def update_lastNo_in_json(lastNo):
    with open('latest.json', 'w') as json_file:
        json.dump({"lastNo": lastNo}, json_file, indent=4)

# ✅ 사람인 공고 크롤링 함수
def crawl_saramin():
    job_data = []
    
    for i in range(1, 4):  # 페이지 1~3 크롤링 (원하면 더 늘려도 됨)
        print(f"📄 {i} 페이지 크롤링 중...")
        url = f'https://www.saramin.co.kr/zf_user/jobs/public/list?page={i}&exp_cd=1&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&cat_mcls=2&panel_type=domestic&search_optional_item=y&search_done=y&panel_count=y&preview=y'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        request = Request(url, headers=headers)
        response = urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        job_listings = soup.select('.list_item')

        for job in job_listings:
            # ✅ 공고 ID(rec_idx) 추출
            job_link_tag = job.select_one('.notification_info .job_tit .str_tit')
            job_link = job_link_tag['href'] if job_link_tag else None
            rec_idx = int(job_link.split('rec_idx=')[-1].split('&')[0]) if job_link else 0  # 정수 변환

            # ✅ 기타 정보 추출
            job_title = job_link_tag.get_text(strip=True) if job_link_tag else "정보 없음"
            company = job.select_one('.company_nm .str_tit')
            company_name = company.get_text(strip=True) if company else "정보 없음"
            work_place = job.select_one('.recruit_info .work_place')
            work_place_text = work_place.get_text(strip=True) if work_place else "정보 없음"
            
            job_sector = job.select_one('.job_sector')  
            job_sector_text = job_sector.get_text(strip=True).replace("\n", ", ") if job_sector else "정보 없음"
            
            full_job_link = f"https://www.saramin.co.kr{job_link}" if job_link else "정보 없음"

            job_data.append({
                "rec_idx": rec_idx,
                "기업명": company_name,
                "공고 제목": job_title,
                "근무지": work_place_text,
                "직무": job_sector_text,
                "링크": full_job_link
            })

        time.sleep(1)  

    return job_data

# ✅ 이메일 발송 함수
def send_email(new_jobs):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = f"[사람인] 신규 채용 공고 {len(new_jobs)}건 업데이트!"
    
    # 📌 HTML 테이블 생성
    body = "<h2>📢 신규 채용 공고 리스트</h2>"
    body += "<table border='1' cellpadding='5' cellspacing='0'>"
    body += "<tr><th>기업명</th><th>공고 제목</th><th>근무지</th><th>직무</th><th>링크</th></tr>"
    for job in new_jobs:
        body += f"<tr><td>{job['기업명']}</td><td>{job['공고 제목']}</td><td>{job['근무지']}</td><td>{job['직무']}</td><td><a href='{job['링크']}'>공고 보기</a></td></tr>"

    body += "</table>"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_SENDER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())
        server.quit()
        print("✅ 이메일 발송 완료!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

# ✅ 실행 함수 (lastNo 비교 & 이메일 발송)
def run():
    lastNo = get_lastNo_from_json()
    print(f"🔍 현재 저장된 lastNo: {lastNo}")

    # ✅ 크롤링 실행
    job_data = crawl_saramin()

    # ✅ lastNo보다 큰 공고 필터링
    new_jobs = [job for job in job_data if job['rec_idx'] > lastNo]

    if new_jobs:
        print(f"✅ 신규 공고 {len(new_jobs)}건 발견! 이메일 전송...")
        send_email(new_jobs)

        # ✅ 최신 공고 ID 저장
        max_rec_idx = max([job['rec_idx'] for job in new_jobs])
        update_lastNo_in_json(max_rec_idx)
    else:
        print("🔍 새로운 공고 없음.")

# 실행
run()
