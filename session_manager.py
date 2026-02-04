import requests
from bs4 import BeautifulSoup
import re
import time

class SessionManager:
    def __init__(self, username, password, base_url="http://139.99.63.204/ints"):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.session = requests.Session()
        self.is_logged_in = False

    def solve_captcha(self, text):
        # البحث عن نمط "What is 5 + 4 = ?"
        match = re.search(r"What is (\d+) \+ (\d+) = \?", text)
        if match:
            num1 = int(match.group(1))
            num2 = int(match.group(2))
            return num1 + num2
        return None

    def login(self):
        try:
            # 1. الحصول على صفحة تسجيل الدخول لجلب الكابتشا
            response = self.session.get(f"{self.base_url}/login")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # حل الكابتشا من نص الصفحة
            captcha_result = self.solve_captcha(response.text)
            if captcha_result is None:
                return False, "لم يتم العثور على الكابتشا في الصفحة"

            # 2. إرسال بيانات تسجيل الدخول
            login_data = {
                "username": self.username,
                "password": self.password,
                "capt": captcha_result
            }
            
            # إرسال الطلب إلى رابط signin
            post_response = self.session.post(f"{self.base_url}/signin", data=login_data)
            
            # التحقق من نجاح تسجيل الدخول (عادة يتم التوجيه إلى Dashboard)
            if "Dashboard" in post_response.text or post_response.status_code == 200:
                # التحقق الإضافي من وجود اسم المستخدم في الصفحة
                if self.username in post_response.text:
                    self.is_logged_in = True
                    return True, "تم تسجيل الدخول بنجاح"
            
            return False, "فشل تسجيل الدخول، تحقق من البيانات أو الكابتشا"
        except Exception as e:
            return False, f"خطأ أثناء الاتصال: {str(e)}"

    def get_messages(self):
        if not self.is_logged_in:
            return []
        try:
            response = self.session.get(f"{self.base_url}/agent/SMSTestPanel")
            soup = BeautifulSoup(response.text, 'html.parser')
            # البحث عن الجدول الثاني (Recent SMS Test)
            tables = soup.find_all('table')
            if len(tables) < 2:
                return []
            
            messages = []
            rows = tables[1].find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    messages.append({
                        "date": cols[0].text.strip(),
                        "range": cols[1].text.strip(),
                        "number": cols[2].text.strip(),
                        "cli": cols[3].text.strip(),
                        "sms": cols[4].text.strip()
                    })
            return messages
        except Exception:
            return []

    def find_code_for_number(self, target_number):
        messages = self.get_messages()
        for m in messages:
            if target_number in m['number']:
                # استخراج الكود (عادة يكون أرقام)
                code_match = re.search(r'(\d{4,8})', m['sms'])
                if code_match:
                    return code_match.group(1), m['sms']
                return None, m['sms']
        return None, None

if __name__ == "__main__":
    # تجربة سريعة
    sm = SessionManager("almoz3j", "hamoalmoz3j")
    success, msg = sm.login()
    print(f"Status: {success}, Message: {msg}")
    if success:
        msgs = sm.get_messages()
        print(f"Found {len(msgs)} messages")
