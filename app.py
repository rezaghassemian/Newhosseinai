from flask import Flask, request, render_template_string, session
from hazm import Normalizer
import sympy
from sympy import symbols, solve, Eq
from langdetect import detect
import re
import os

# Workaround for Pydroid: Ensure required packages are installed
try:
    import hazm
except ImportError:
    os.system("pip install hazm")
    import hazm

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Random secret key for sessions

# Simplified NLP setup
normalizer = Normalizer()

# Minimal FAQ (Persian)
FAQ = {
    "ساخته شدی؟": "من در سال 2024 ساخته شدم!",
    "کمک می‌کنی؟": "بله! سوالات ریاضی بپرسید مثل: 'مساحت مربع با ضلع ۵' یا 'حل کن ۲x=۱۰'"
}

# Deployment-friendly configuration
HOST = '0.0.0.0'
PORT = 5000

HTML = '''
<!DOCTYPE html>
<html lang="fa">
<!-- Keep your existing HTML template here -->
</html>
'''

def get_response(text):
    text = normalizer.normalize(text.strip())
    
    # FAQ Check
    if text in FAQ:
        return FAQ[text]
    
    # Math: Simple operations
    if 'مساحت مربع' in text:
        nums = re.findall(r'\d+', text)
        return f"مساحت: {int(nums[0])**2}" if nums else "لطفاً عدد ضلع را بگویید."
    
    # Equation solving
    if 'حل کن' in text and '=' in text:
        try:
            x = symbols('x')
            eq_parts = text.split('حل کن')[-1].split('=')
            eq = Eq(eval(eq_parts[0].strip()), eval(eq_parts[1].strip()))
            return f"پاسخ: x = {solve(eq, x)[0]}"
        except:
            return "معادله نامعتبر است"
    
    # Fallback
    return "متوجه نشدم. مثال: 'مساحت مربع با ضلع ۵' یا 'حل کن ۲x=۱۰'"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_msg = request.form.get("msg", "")
        response = get_response(user_msg)
        return render_template_string(HTML, user_msg=user_msg, response=response)
    return render_template_string(HTML)

if __name__ == "__main__":
    # Production-ready configuration
    app.run(host=HOST, port=PORT)