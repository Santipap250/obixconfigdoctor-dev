from flask import Flask, render_template, request

app = Flask(__name__)

def analyze_drone(size, battery, style, mode):
    analysis = {}

    # ===== OVERVIEW =====
    analysis["overview"] = (
        f"โดรนขนาด {size} นิ้ว ใช้แบต {battery} "
        f"เน้นการบินสไตล์ {style} เหมาะกับการตั้งค่าแบบ {mode}"
    )

    # ===== BASIC TIPS =====
    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดต้องไม่บิดงอ",
        "ขันน็อตมอเตอร์ให้แน่น",
        "เช็คจุดบัดกรี ESC และแบตเตอรี่"
    ]

    # ===== ADVANCED / PRO =====
    if mode in ["Advanced", "Pro"]:
        if style == "Freestyle":
            pid = {"P": 48, "I": 52, "D": 38}
            filter_desc = "กรองบาลานซ์ระหว่างความหนึบและความไว เหมาะกับการกระชากคันเร่ง"
            extra = "เหมาะกับการตีท่าหนัก ๆ แต่ควรเช็คอุณหภูมิมอเตอร์"

        elif style == "Racing":
            pid = {"P": 55, "I": 45, "D": 42}
            filter_desc = "กรองต่ำ Latency ต่ำ ควบคุมแม่นยำ"
            extra = "เน้นความไว หลีกเลี่ยงใบพัดอ่อน"

        elif style == "Long Range":
            pid = {"P": 42, "I": 50, "D": 32}
            filter_desc = "กรอง Noise สูง ภาพนิ่ง มอเตอร์เย็น"
            extra = (
                "แนะนำ Throttle Limit 80–85% | "
                "Battery Warning 3.5V | Critical 3.3V"
            )

        analysis["advanced"] = {
            "PID": pid,
            "Filter": filter_desc,
            "ExtraTips": extra
        }

    return analysis


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    if request.method == "POST":
        size = request.form["size"]
        battery = request.form["battery"]
        style = request.form["style"]
        mode = request.form["mode"]

        analysis = analyze_drone(size, battery, style, mode)

    return render_template("index.html", analysis=analysis)


if __name__ == "__main__":
    app.run(debug=True)
