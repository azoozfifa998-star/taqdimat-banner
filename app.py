from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
import qrcode
from colorthief import ColorThief
import io
import os

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_banner():
    data = request.json
    
    title = data.get('title', '')
    org = data.get('org', '')
    city = data.get('city', '')
    deadline = data.get('deadline', '')
    benefits = data.get('benefits', '')
    apply_url = data.get('apply_url', '')
    logo_url = data.get('logo_url', '')
    
    # تحميل الشعار
    try:
        logo_response = requests.get(logo_url, timeout=10)
        logo_img = Image.open(io.BytesIO(logo_response.content)).convert('RGBA')
        ct = ColorThief(io.BytesIO(logo_response.content))
        dominant_color = ct.get_color(quality=1)
    except:
        logo_img = None
        dominant_color = (30, 80, 160)
    
    # إنشاء البانر
    width, height = 1024, 1024
    img = Image.new('RGB', (width, height), color=dominant_color)
    draw = ImageDraw.Draw(img)
    
    # خلفية فاتحة في المنتصف
    draw.rectangle([40, 200, width-40, height-40], fill=(255,255,255,230))
    
    # إضافة الشعار
    if logo_img:
        logo_img.thumbnail((150, 150))
        logo_pos = ((width - logo_img.width) // 2, 30)
        img.paste(logo_img, logo_pos, logo_img)
    
    # QR Code
    qr = qrcode.make(apply_url)
    qr = qr.resize((150, 150))
    img.paste(qr, (width-190, height-190))
    
    # حفظ وإرسال
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
