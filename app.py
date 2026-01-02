from flask import Flask, render_template, request
from analyzer.prop_logic import analyze_propeller
from analyzer.thrust_logic import calculate_thrust_weight, estimate_battery_runtime
from analyzer.battery_logic import analyze_battery
import logging, csv, os, datetime

app = Flask(__name__)

# Setup logger
logdir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logdir, exist_ok=True)
logfile = os.path.join(logdir, "app.log")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler(logfile, encoding="utf-8"),
                              logging.StreamHandler()])

# CSV analytics file
csv_path = os.path.join(logdir, "analytics.csv")
if not os.path.exists(csv_path):
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp","size_in","weight_g","battery","style","prop_size","blades","pitch","thrust_ratio","battery_est_min"])

# logic analyze
def analyze_drone(size, battery, style, prop_result, weight):
    analysis = {}
    analysis["overview"] = f'โดรน {size}" แบต {battery}, สไตล์ {style}, ใบพัด: {prop_result["summary"]}'
    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดไม่บิดงอ",
        "ขันน็อตมอเตอร์ให้แน่น",
        "เช็คจุดบัดกรี ESC และแบตเตอรี่"
    ]

    if style == "freestyle":
        pid = {...}  # keep your PID sets or paste full dict from your preferred values
    # For brevity, fill with your existing PID objects:
    pid = {
        "roll": {"p":48,"i":52,"d":38},
        "pitch":{"p":48,"i":52,"d":38},
        "yaw":{"p":40,"i":45,"d":0}
    }
    if style == "racing":
        pid = {
            "roll":55, "pitch":55
        } # replace with actual full dict if needed

    # choose filters per style
    if style == "freestyle":
        filter_desc = {"gyro_lpf2":90,"dterm_lpf1":120,"dyn_notch":2}
        extra_tips = ["Freestyle – สมดุล บินสนุก"]
    elif style == "racing":
        filter_desc = {"gyro_lpf2":120,"dterm_lpf1":150,"dyn_notch":3}
        extra_tips = ["Racing – ตอบสนองไว"]
    else:
        filter_desc = {"gyro_lpf2":70,"dterm_lpf1":90,"dyn_notch":1}
        extra_tips = ["Long Range – นิ่ง ประหยัดแบต"]

    analysis["pid"] = pid
    analysis["filter"] = filter_desc
    analysis["extra_tips"] = extra_tips
    analysis["thrust_ratio"] = calculate_thrust_weight(prop_result["effect"]["motor_load"], weight)
    analysis["battery_est"] = estimate_battery_runtime(weight, battery)

    return analysis

# routes
@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/ping")
def ping():
    return "pong"

@app.route("/app", methods=["GET","POST"])
def index():
    analysis = None
    try:
        if request.method == "POST":
            size = float(request.form["size"])
            battery = request.form["battery"]
            style = request.form["style"]
            weight = float(request.form.get("weight", 1000))  # grams
            prop_size = float(request.form["prop_size"])
            blade_count = int(request.form["blades"])
            prop_pitch = float(request.form["pitch"])

            prop_result = analyze_propeller(prop_size, prop_pitch, blade_count, style)
            analysis = analyze_drone(size, battery, style, prop_result, weight)
            analysis["prop_result"] = prop_result

            # write analytics row
            with open(csv_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.datetime.utcnow().isoformat(),
                    size, weight, battery, style, prop_size, blade_count, prop_pitch,
                    analysis.get("thrust_ratio"), analysis.get("battery_est")
                ])

            logging.info(f"analysis: size={size} battery={battery} style={style} prop={prop_result['summary']}")
    except Exception as e:
        logging.exception("Error in /app")
        # show friendly page with error
        return render_template("error.html", error=str(e)), 500

    return render_template("index.html", analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)