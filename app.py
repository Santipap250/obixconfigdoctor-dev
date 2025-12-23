from flask import Flask, render_template, request
from analyzer.prop_logic import analyze_propeller

app = Flask(__name__)

def analyze_drone(size, battery, style, prop_size, blades, pitch):
    # ===== วิเคราะห์ใบพัด =====
    prop_analysis = analyze_propeller(
        prop_size=prop_size,
        prop_pitch=pitch,
        blade_count=blades,
        style=style
    )

    # ===== PID / Filter ตัวอย่าง =====
    if style == "freestyle":
        pid = {"roll": {"p":48,"i":52,"d":38},
               "pitch":{"p":48,"i":52,"d":38},
               "yaw":{"p":40,"i":45,"d":0}}
        filter_data = {"gyro_lpf2":90, "dterm_lpf1":150, "dyn_notch":1}
        extra_tips = ["บินสมดุล แรงพอดี","เช็คความร้อนมอเตอร์"]
    elif style == "racing":
        pid = {"roll": {"p":55,"i":45,"d":42},
               "pitch":{"p":55,"i":45,"d":42},
               "yaw":{"p":50,"i":40,"d":0}}
        filter_data = {"gyro_lpf2":120, "dterm_lpf1":180, "dyn_notch":2}
        extra_tips = ["ตอบสนองไว","เหมาะสาย Racing"]
    else:  # longrange
        pid = {"roll": {"p":42,"i":50,"d":32},
               "pitch":{"p":42,"i":50,"d":32},
               "yaw":{"p":40,"i":45,"d":0}}
        filter_data = {"gyro_lpf2":60, "dterm_lpf1":100, "dyn_notch":1}
        extra_tips = ["บินนุ่ม ประหยัดแบต","คุมง่าย"]

    analysis = {
        "overview": f"โดรน {size}\" แบต {battery} สไตล์ {style}",
        "basic_tips": ["ตรวจสอบใบพัด","ขันน็อตมอเตอร์","เช็คจุดบัดกรี ESC/แบตเตอรี่"],
        "pid": pid,
        "filter": filter_data,
        "extra_tips": extra_tips,
        "prop_analysis": prop_analysis
    }

    return analysis


@app.route("/", methods=["GET","POST"])
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
