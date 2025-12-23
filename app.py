from flask import Flask, render_template, request
from analyzer.prop_logic import analyze_propeller

app = Flask(__name__)

def analyze_drone(size, battery, style, prop_size, blades, pitch):
    analysis = {}

    # ===== OVERVIEW =====
    analysis["overview"] = f"โดรนขนาด {size} นิ้ว แบต {battery} สไตล์ {style}"

    # ===== BASIC TIPS =====
    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดต้องไม่บิดงอ",
        "ขันน็อตมอเตอร์ให้แน่น",
        "เช็คจุดบัดกรี ESC และแบตเตอรี่"
    ]

    # ===== PID / Filter (Dummy ตัวอย่าง) =====
    pid = {
        "roll": {"p": 48, "i": 52, "d": 38},
        "pitch": {"p": 48, "i": 52, "d": 38},
        "yaw": {"p": 40, "i": 45}
    }
    filter_cfg = {
        "gyro_lpf2": 90,
        "dterm_lpf1": 100,
        "dyn_notch": 2
    }
    extra_tips = [
        "ทดสอบบินสั้น ๆ หลังตั้งค่า",
        "เช็คความร้อนมอเตอร์หลังบิน"
    ]

    analysis["pid"] = pid
    analysis["filter"] = filter_cfg
    analysis["extra_tips"] = extra_tips

    # ===== Propeller Analysis =====
    analysis["prop"] = analyze_propeller(
        prop_size=prop_size,
        prop_pitch=pitch,
        blade_count=blades,
        style=style
    )

    # ===== Thrust-to-Weight & Battery Estimate =====
    weight_grams = size * 180  # dummy weight
    thrust_total = prop_size * blades * 100  # dummy thrust
    tw_ratio = round(thrust_total / weight_grams, 2)
    battery_capacity = 1500 if battery=="4S" else 2200
    runtime_min = round((battery_capacity / 1500) * 3.5, 1)  # dummy runtime
    analysis["tw_ratio"] = tw_ratio
    analysis["battery_runtime"] = runtime_min

    return analysis


@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    if request.method == "POST":
        size = int(request.form["size"])
        battery = request.form["battery"]
        style = request.form["style"]

        prop_size = float(request.form["prop_size"])
        blades = int(request.form["blades"])
        pitch = float(request.form["pitch"])

        analysis = analyze_drone(size, battery, style, prop_size, blades, pitch)

    return render_template("index.html", analysis=analysis)


if __name__ == "__main__":
    app.run(debug=True)
