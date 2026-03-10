from flask import Flask, request, jsonify
from PIL import Image, ImageDraw
import requests
import qrcode
from colorthief import ColorThief
import io
import os
import base64

app = Flask(__name__)

IMGBB_KEY = "0b973e925d4f4470cee367bcfccfcd13"

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
    
    # تحميل الشعار واستخراج اللون
    try:
        logo_response = requests.get(logo_url, timeout=10)
        logo_bytes = logo_response.content
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert('RGBA')
        ct = ColorThief(io.BytesIO(logo_bytes))
        dominant_color = ct.get_color(quality=1)
    except:
        logo_img = None
        dominant_color = (30, 80, 160)
    
    # إنشاء البانر
    width, height = 1024, 1024
    img = Image.new('RGB', (width, height), color=dominant_color)
    draw = ImageDraw.Draw(img)
    
    # خلفية بيضاء
    draw.rectangle([40, 200, width-40, height-160], fill=(255, 255, 255))
    
    # شعار الجهة
    if logo_img:
        logo_img.thumbnail((150, 150))
        logo_x = (width - logo_img.width) // 2
        img.paste(logo_img, (logo_x, 30), logo_img)
    
    # QR Code
    try:
        qr = qrcode.make(apply_url)
        qr = qr.resize((160, 160))
        img.paste(qr, (width - 200, height - 200))
    except:
        pass
    
    # رفع لـ imgbb
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    img_base64 = base64.b64encode(output.read()).decode('utf-8')
    
    try:
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': IMGBB_KEY,
                'image': img_base64
            }
        )
        result = response.json()
        image_url = result['data']['url']
    except:
        image_url = ''
    
    return jsonify({'url': image_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
