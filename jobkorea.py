import os
import json
import time
import smtplib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ✅ JSON에서 lastNo 불러오기 (잡코리아)
def get_lastNo_from_json():
    try:
        with open('latest_jobkorea.json', 'r') as json_file:
            data = json.load(json_file)
            return data.get("lastNo", 0)
    except FileNotFoundError:
        return 0  # 파일이 없으면 기본값 0
# ✅ JSON에 lastNo 업데이트 (잡코리아)
def update_lastNo_in_json(lastNo):
    with open('latest_jobkorea.json', 'w') as json_file:
        json.dump({"lastNo": lastNo}, json_file, indent=4)

# ✅ 잡코리아 공고 크롤링 함수
def crawl_jobkorea():
    job_data = []

    # ✅ 기본 URL (백엔드 개발자, 웹 개발자, 시스템 엔지니어, 소프트웨어 개발자, 신입 포함)
    BASE_URL = "https://www.jobkorea.co.kr/Search/?stext=%EB%B0%B1%EC%97%94%EB%93%9C%20%EA%B0%9C%EB%B0%9C%EC%9E%90&duty=1000229%2C1000231%2C1000239%2C1000233&careerType=1&tabType=recruit&Page_No={}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for i in range(1, 4):  # ✅ 1~3 페이지 크롤링
        print(f"📄 잡코리아 {i} 페이지 크롤링 중...")
        url = BASE_URL.format(i)

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        job_listings = soup.select('.list-item')  # ✅ 공고 리스트 가져오기

        for job in job_listings:
            # ✅ 공고 ID(rec_idx) 추출
            rec_idx = int(job['data-gno']) if 'data-gno' in job.attrs else 0

            # ✅ 기업명 추출
            company_tag = job.select_one('.list-section-corp .corp-name-link')
            company_name = company_tag.get_text(strip=True) if company_tag else "정보 없음"

            # ✅ 공고 제목 추출
            job_title_tag = job.select_one('.list-section-information .information-title-link')
            job_title = job_title_tag.get_text(strip=True) if job_title_tag else "정보 없음"

            # ✅ 근무지 추출
            work_place_tag = job.select_one('.chip-information-group .chip-information-item:nth-of-type(4)')
            work_place_text = work_place_tag.get_text(strip=True) if work_place_tag else "정보 없음"

            # ✅ 직무 추출
            job_sector_tag = job.select_one('.list-section-information .information-title')
            job_sector_text = job_sector_tag.get_text(strip=True).replace("\n", ", ") if job_sector_tag else "정보 없음"

            # ✅ 공고 링크 생성
            job_link = f"https://www.jobkorea.co.kr/Recruit/GI_Read/{rec_idx}" if rec_idx else "정보 없음"

            job_data.append({
                "rec_idx": rec_idx,
                "기업명": company_name,
                "공고 제목": job_title,
                "근무지": work_place_text,
                "직무": job_sector_text,
                "링크": job_link
            })

        time.sleep(1)  # ✅ 서버 부하 방지

    return job_data

# ✅ 이메일 발송 함수 (잡코리아)
def send_email(new_jobs):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = f"[잡코리아] 신규 채용 공고 {len(new_jobs)}건 업데이트!"
    
    # 📌 HTML 테이블 생성
    body = "<h2>📢 잡코리아 신규 채용 공고 리스트</h2>"
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

# ✅ 실행 함수
def run():
    lastNo = get_lastNo_from_json()
    print(f"🔍 현재 저장된 lastNo (잡코리아): {lastNo}")

    job_data = crawl_jobkorea()
    new_jobs = [job for job in job_data if job['rec_idx'] > lastNo]

    if new_jobs:
        print(f"✅ 신규 공고 {len(new_jobs)}건 발견! 이메일 전송...")
        send_email(new_jobs)
        update_lastNo_in_json(max(job['rec_idx'] for job in new_jobs))
    else:
        print("🔍 새로운 공고 없음.")

# 실행
run()
