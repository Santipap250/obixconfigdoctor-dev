from flask import Flask, render_template, request

app = Flask(__name__)

def analyze_drone(size, battery, style):
    analysis = {}

    # ===== OVERVIEW =====
    analysis["overview"] = (
        f"โดรนขนาด {size} นิ้ว ใช้แบต {battery} "
        f"สไตล์ {style.upper()} เหมาะกับการตั้งค่าเฉพาะทาง"
    )

    # ===== BASIC TIPS =====
    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดต้องไม่บิดงอ",
        "ขันน็อตมอเตอร์และ stack ให้แน่น",
        "สาย ESC และแบตไม่ควรยาวเกินไป"
    ]

    # ===== CONFIG BY STYLE =====
    if style == "freestyle":
        pid = {
            "roll":  {"p": 48, "i": 52, "d": 38},
            "pitch": {"p": 50, "i": 54, "d": 40},
            "yaw":   {"p": 45, "i": 50, "d": 0}
        }
        filter_cfg = {
            "gyro_lpf2": 300,
            "dterm_lpf1": 120,
            "dyn_notch": 2
        }
        extra = [
            "เหมาะกับการตีท่า Freestyle",
            "บาลานซ์ความหนึบและความไว",
            "เช็กอุณหภูมิมอเตอร์หลังบิน"
        ]

    elif style == "longrange":
        pid = {
            "roll":  {"p": 42, "i": 48, "d": 30},
            "pitch": {"p": 44, "i": 50, "d": 32},
            "yaw":   {"p": 40, "i": 45, "d": 0}
        }
        filter_cfg = {
            "gyro_lpf2": 200,
            "dterm_lpf1": 90,
            "dyn_notch": 3
        }
        extra = [
            "ภาพนิ่ง ประหยัดแบต",
            "แนะนำ Throttle Limit 80–85%",
            "เหมาะกับ Cinematic / Long Range"
        ]

    elif style == "racing":
        pid = {
            "roll":  {"p": 55, "i": 45, "d": 42},
            "pitch": {"p": 58, "i": 48, "d": 45},
            "yaw":   {"p": 50, "i": 45, "d": 0}
        }
        filter_cfg = {
            "gyro_lpf2": 350,
            "dterm_lpf1": 150,
            "dyn_notch": 1
        }
        extra = [
            "Latency ต่ำ ตอบสนองไวมาก",
            "เหมาะกับสนามแข่ง",
            "ใช้ใบพัดแข็งจะได้ผลดีที่สุด"
        ]

    analysis["pid"] = pid
    analysis["filter"] = filter_cfg
    analysis["extra_tips"] = extra

    return analysis


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    if request.method == "POST":
        size = request.form["size"]
        battery = request.form["battery"]
        style = request.form["style"]

        analysis = analyze_drone(size, battery, style)

    return render_template("index.html", analysis=analysis)


if __name__ == "__main__":
    app.run(debug=True)
