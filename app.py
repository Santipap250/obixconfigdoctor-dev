from flask import Flask, render_template, request

app = Flask(__name__)

def analyze_drone(size, battery, style, mode):
    result = {}
    result['overview'] = f"โดรน {size} นิ้ว + {battery} + {style} → เหมาะกับการบิน"
    
    # Basic tips
    result['basic_tips'] = [
        "Throttle limit 90%",
        "ตรวจสอบความร้อนมอเตอร์",
        "ใช้ prop ใบไม่จัดเกิน"
    ]
    
    # Advanced / Pro tips
    if mode in ['Advanced', 'Pro']:
        pid_base = 40 if mode=='Advanced' else 45
        result['advanced'] = {
            'PID': {
                'P': pid_base + int(size),
                'I': 30 if mode=='Advanced' else 35,
                'D': 20 if mode=='Advanced' else 25
            },
            'Filter': "Lowpass 80Hz / 90Hz, Notch 150Hz / 180Hz" if mode=='Advanced' else "Lowpass 90Hz, Notch 180Hz",
            'ExtraTips': "ปรับ D-term ลด 5–10% สำหรับ Freestyle" if mode=='Advanced' else "ใช้ prop เบา + ปรับ RPM motor ให้เข้ากับแบตเตอรี่"
        }

    # Fun fact / info section
    result['info'] = [
        "การตั้งค่า PID และ Filter ให้เหมาะสมช่วยลดอาการสั่นและกินไฟน้อยลง",
        "Advanced/Pro ช่วยให้สามารถปรับ fine-tuning สำหรับสไตล์การบินเฉพาะตัว",
        "สำหรับมือใหม่ แนะนำใช้ Basic ก่อน"
    ]

    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    analysis = None
    if request.method == 'POST':
        size = request.form.get('size')
        battery = request.form.get('battery')
        style = request.form.get('style')
        mode = request.form.get('mode')
        analysis = analyze_drone(size, battery, style, mode)
    return render_template('index.html', analysis=analysis)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
