from flask import Flask, render_template, request

app = Flask(__name__)

def analyze_drone(size, battery, style, mode):
    analysis = {}

    # ===== OVERVIEW =====
    analysis["overview"] = (
        f"โดรนขนาด {size} นิ้ว | แบต {battery} | "
        f"สไตล์ {style.upper()} | โหมด {mode}"
    )

    # ===== BASIC TIPS =====
    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดต้องไม่บิดงอ",
        "ขันน็อตมอเตอร์ให้แน่น",
        "ESC และสายแบตต้องไม่มีรอยไหม้",
        "เช็ค Gyro noise ก่อนบินจริง"
    ]

    # ===== ADVANCED / PRO =====
    if mode in ["Advanced", "Pro"]:

        if style == "freestyle":
            pid = {
                "Roll":  {"P": 50, "I": 55, "D": 38},
                "Pitch": {"P": 54, "I": 58, "D": 42},
                "Yaw":   {"P": 45, "I": 60, "D": 0}
            }
            filter_cfg = {
                "Gyro": "PT1 90Hz",
                "Dterm": "PT1 80Hz",
                "RPM_Filter": "ON",
                "Dynamic_Notch": "ON"
            }
            extra = "หนึบ คุมง่าย เหมาะกับท่าหนัก / ต้องเช็คมอเตอร์อุ่นหรือไม่"

        elif style == "racing":
            pid = {
                "Roll":  {"P": 58, "I": 48, "D": 45},
                "Pitch": {"P": 62, "I": 52, "D": 48},
                "Yaw":   {"P": 50, "I": 65, "D": 0}
            }
            filter_cfg = {
                "Gyro": "PT1 120Hz",
                "Dterm": "PT1 100Hz",
                "RPM_Filter": "ON",
                "Dynamic_Notch": "OFF"
            }
            extra = "Latency ต่ำมาก เหมาะแข่ง แนะนำใช้ใบแข็ง"

        elif style == "longrange":
            pid = {
                "Roll":  {"P": 42, "I": 60, "D": 30},
                "Pitch": {"P": 45, "I": 65, "D": 32},
                "Yaw":   {"P": 38, "I": 70, "D": 0}
            }
            filter_cfg = {
                "Gyro": "PT1 70Hz",
                "Dterm": "PT1 65Hz",
                "RPM_Filter": "ON",
                "Dynamic_Notch": "ON"
            }
            extra = (
                "มอเตอร์เย็น ประหยัดแบต | "
                "Throttle Limit 80–85% | "
                "VBAT Warning 3.5V / Critical 3.3V"
            )

        elif style == "smooth":
            pid = {
                "Roll":  {"P": 46, "I": 58, "D": 34},
                "Pitch": {"P": 50, "I": 62, "D": 36},
                "Yaw":   {"P": 42, "I": 68, "D": 0}
            }
            filter_cfg = {
                "Gyro": "PT1 80Hz",
                "Dterm": "PT1 75Hz",
                "RPM_Filter": "ON",
                "Dynamic_Notch": "ON"
            }
            extra = "ภาพนิ่ง Cinematic เหมาะถ่ายวิดีโอ"

        analysis["advanced"] = {
            "PID": pid,
            "Filter": filter_cfg,
            "ExtraTips": extra
        }

    return analysis


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None

    if request.method == "POST":
        size = float(request.form["size"])
        battery = request.form["battery"]
        style = request.form["style"]
        mode = request.form["mode"]

        analysis = analyze_drone(size, battery, style, mode)

    return render_template("index.html", analysis=analysis)


if __name__ == "__main__":
    app.run()
