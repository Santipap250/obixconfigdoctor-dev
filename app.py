#!/usr/bin/env python3
import os
import logging
from flask import Flask, render_template, request, redirect, url_for

# ----------------- app init -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obix")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")

# ----------------- optional imports -----------------
try:
    from analyzer.prop_logic import analyze_propeller
except Exception:
    analyze_propeller = None

try:
    from logic.doctor import analyze_drone
except Exception:
    analyze_drone = None

# ----------------- helpers -----------------
def parse_float(form, key, default=None):
    try:
        return float(form.get(key, default))
    except Exception:
        return default

def parse_int(form, key, default=None):
    try:
        return int(form.get(key, default))
    except Exception:
        return default

def safe_analysis(a):
    if not isinstance(a, dict):
        a = {}

    a.setdefault('style', '-')
    a.setdefault('weight_class', '-')
    a.setdefault('thrust_ratio', 0)
    a.setdefault('flight_time', 0)
    a.setdefault('summary', '-')
    a.setdefault('basic_tips', [])

    a.setdefault('pid', {
        'roll': {'p': 0, 'i': 0, 'd': 0},
        'pitch': {'p': 0, 'i': 0, 'd': 0},
        'yaw': {'p': 0, 'i': 0}
    })

    a.setdefault('filter', {
        'gyro_lpf2': 0,
        'dterm_lpf1': 0,
        'dyn_notch': 'OFF'
    })

    a.setdefault('prop_result', {
        'summary': '-',
        'effect': {
            'noise': 0,
            'motor_load': 0,
            'grip': '-'
        },
        'recommendation': '-'
    })

    return a

# ----------------- routes -----------------
@app.route('/ping')
def ping():
    return 'pong', 200

@app.route('/')
def root():
    return redirect(url_for('app_page'))

@app.route('/app', methods=['GET', 'POST'])
def app_page():
    analysis = None
    errors = []

    if request.method == 'POST':
        try:
            size = parse_float(request.form, 'size', 5)
            weight = parse_float(request.form, 'weight', 500)
            battery = request.form.get('battery', '4S')
            style = request.form.get('style', 'freestyle')

            prop_size = parse_float(request.form, 'prop_size', 5)
            blades = parse_int(request.form, 'blades', 3)
            pitch = parse_float(request.form, 'pitch', 4)

            if analyze_propeller:
                prop_result = analyze_propeller(prop_size, pitch, blades, style)
            else:
                prop_result = {}

            if analyze_drone:
                analysis = analyze_drone(size, battery, style, prop_result, weight)
                analysis['prop_result'] = prop_result
            else:
                analysis = {'prop_result': prop_result}

        except Exception as e:
            logger.exception("analysis failed")
            errors.append("เกิดข้อผิดพลาดภายในระบบ")

    analysis = safe_analysis(analysis)
    return render_template("index.html", analysis=analysis, errors=errors)

# ----------------- run -----------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )