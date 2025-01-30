## 사람인 & 잡코리아 크롤러
**사람인(Saramin)** 및 **잡코리아(JobKorea)** 에서 **백엔드 개발자 채용 공고를 크롤링**하여,

**신규 공고가 있을 경우 이메일로 자동 발송**하는 Python 스크립트

---

## 📂 **파일 설명**

| 파일명 | 설명 |
| --- | --- |
| `saramin.py` | 사람인 채용 공고 크롤러 (신규 공고가 있으면 이메일 발송) |
| `jobkorea.py` | 잡코리아 채용 공고 크롤러 (신규 공고가 있으면 이메일 발송) |
| `latest.json` | 사람인에서 저장된 최신 공고 ID |
| `latest_jobkorea.json` | 잡코리아에서 저장된 최신 공고 ID |

---

## ⚙️ **설정 변경 방법**

### **1️⃣ 크롤링 URL 변경**

각 스크립트의 `BASE_URL` 또는 `url` 값을 변경하면 **다른 필터 조건**을 적용할 수 있습니다.

예를 들어, **프론트엔드 개발자, 데이터 엔지니어 등 다른 직군**을 추가하고 싶다면,

각 사이트에서 원하는 조건을 검색한 후 **URL을 수정하면 적용 가능합니다**.

📌 **각자 원하는 필터를 적용한 후, 본인에게 맞게 URL을 수정해서 사용하면 됩니다.**

---

### **2️⃣ 이메일 발송 설정 변경**

- 발송할 **이메일 주소 및 비밀번호를 본인에 맞게 수정해야 합니다**.
- 수신자 이메일 주소도 원하는 대로 변경할 수 있습니다.

---

## 📌 **주의 사항**

- **크롤링 빈도를 너무 짧게 설정하면 사이트에서 차단될 가능성이 있음** → `time.sleep(1)` 유지 권장.
- **로그를 저장하려면 `>> log.txt 2>&1` 추가 가능**:
    
    ```bash
    bash
    복사편집
    python saramin.py >> saramin.log 2>&1
    
    ```
    
- **EC2에서 자동 실행하려면 크론잡을 설정하면 됨** (원하는 실행 주기에 맞게 조정).

---

## 🎯 **결론**

- 사람인과 잡코리아에서 **백엔드 개발자 공고를 크롤링하여 이메일로 자동 발송**하는 프로젝트입니다.
- 크롤링 URL은 **각자 필터링을 적용한 후, 본인에게 맞게 설정해서 사용하면 됩니다**.
- 이메일 발송 설정 또한 **각자의 메일 계정 정보로 변경해야 정상 작동합니다**.

🚀 **필요한 조건에 맞게 수정하여 원하는 채용 정보를 빠르게 받아보세요!** 🎯
