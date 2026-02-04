import re

# قاموس لبعض رموز الدول وأعلامها (يمكن توسيعه)
COUNTRY_FLAGS = {
    "93": "🇦🇫", # Afghanistan
    "355": "🇦🇱", # Albania
    "213": "🇩🇿", # Algeria
    "376": "🇦🇩", # Andorra
    "244": "🇦🇴", # Angola
    "1": "🇺🇸",   # USA/Canada
    "44": "🇬🇧",  # UK
    "7": "🇷🇺",   # Russia
    "20": "🇪🇬",  # Egypt
    "966": "🇸🇦", # Saudi Arabia
    "971": "🇦🇪", # UAE
    "964": "🇮🇶", # Iraq
    "965": "🇰🇼", # Kuwait
    "968": "🇴🇲", # Oman
    "974": "🇶🇦", # Qatar
    "973": "🇧🇭", # Bahrain
    "962": "🇯🇴", # Jordan
    "961": "🇱🇧", # Lebanon
    "963": "🇸🇾", # Syria
    "212": "🇲🇦", # Morocco
    "216": "🇹🇳", # Tunisia
    "218": "🇱🇾", # Libya
    "249": "🇸🇩", # Sudan
    "967": "🇾🇪", # Yemen
    "970": "🇵🇸", # Palestine
    "58": "🇻🇪",  # Venezuela
    "855": "🇰🇭", # Cambodia
    "243": "🇨🇩", # DRC
}

def get_flag_by_number(number):
    # تنظيف الرقم من أي رموز غير رقمية
    clean_num = re.sub(r'\D', '', str(number))
    
    # محاولة مطابقة أول 3 أرقام، ثم 2، ثم 1
    for length in [3, 2, 1]:
        prefix = clean_num[:length]
        if prefix in COUNTRY_FLAGS:
            return COUNTRY_FLAGS[prefix]
    
    return "🏳️" # علم افتراضي إذا لم يتم العثور على الدولة

def parse_combo(text):
    """
    تحليل الكومبو المرسل (رقم:باسورد أو مجرد أرقام)
    """
    lines = text.strip().split('\n')
    parsed_numbers = []
    for line in lines:
        # البحث عن أي رقم في السطر
        match = re.search(r'(\d{7,15})', line)
        if match:
            num = match.group(1)
            flag = get_flag_by_number(num)
            parsed_numbers.append({"number": num, "flag": flag})
    return parsed_numbers
