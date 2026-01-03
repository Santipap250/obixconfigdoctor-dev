#!/usr/bin/env python3
"""
app.py - production-friendly patched version for OBIXConfigDoctor

Features:
- safe input parsing + validation
- /ping health endpoint for Render
- robust try/except around analysis (no SyntaxError)
- safe_analysis() normalizes output structure for templates
- friendly logging
- uses index.html as app template and loading.html for root
"""
import os
import logging
from flask import Flask, render_template, request, redirect, url_for

# Try imports; keep None if missing so app still starts
try:
    from analyzer.prop_logic import analyze_propeller
except Exception:
    analyze_propeller = None

try:
    from logic.doctor import analyze_drone
except Exception:
    analyze_drone = None

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obix")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")

# ---------- helpers ----------
def parse_float(form, key, default=None, minv=None, maxv=None, required=False):
    raw = form.get(key, None)
    if raw is None or raw == "":
        if required and default is None:
            raise ValueError(f"Field '{key}' is required")
        return default
    try:
        v = float(raw)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{key}' must be a number")
    if minv is not None and v < minv:
        raise ValueError(f"Field '{key}' must be >= {minv}")
    if maxv is not None and v > maxv:
        raise ValueError(f"Field '{key}' must be <= {maxv}")
    return v

def parse_int(form, key, default=None, minv=None, maxv=None, required=False):
    raw = form.get(key, None)
    if raw is None or raw == "":
        if required and default is None:
            raise ValueError(f"Field '{key}' is required")
        return default
    try:
        v = int(raw)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{key}' must be an integer")
    if minv is not None and v < minv:
        raise ValueError(f"Field '{key}' must be >= {minv}")
    if maxv is not None and v > maxv:
        raise ValueError(f"Field '{key}' must be <= {maxv}")
    return v

def safe_analysis(a):
    """
    Ensure `analysis` is a dict and contains all keys templates expect.
    If a is None or not a dict, return a default-safe dict.
    """
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

# ---------- routes ----------
@app.route('/')
def loading():
    # Prefer loading.html if present (should contain redirect JS to /app)
    if os.path.exists(os.path.join(app.root_path, 'templates', 'loading.html')):
        return render_template('loading.html')
    # fallback: redirect to /app
    return redirect(url_for('app_page'))

@app.route('/ping')
def ping():
    # health check for Render (must return 200)
    return 'pong', 200

@app.route('/app', methods=['GET', 'POST'])
def app_page():
    analysis = None
    errors = []

    if request.method == 'POST':
        form = request.form
        try:
            # Parse and validate inputs (tune ranges as needed)
            size = parse_float(form, 'size', default=5.0, minv=0.1, maxv=100.0)
            weight = parse_float(form, 'weight', default=450.0, minv=1.0, maxv=100000.0)
            battery = form.get('battery', '4S')
            style = form.get('style', 'Freestyle')

            prop_size = parse_float(form, 'prop_size', default=5.0, minv=1.0, maxv=30.0)
            blades = parse_int(form, 'blades', default=2, minv=1, maxv=8)
            pitch = parse_float(form, 'pitch', default=3.0, minv=0.1, maxv=12.0)

            # ensure prop analyzer exists
            if analyze_propeller is None:
                raise RuntimeError('analyze_propeller module not found')
            prop_result = analyze_propeller(prop_size, pitch, blades, style)

            # run full analysis in try/except to avoid crashing the app
            try:
                if analyze_drone is None:
                    analysis = {
                        'warning': 'analyze_drone function not found; showing prop_result only',
                        'prop_result': prop_result
                    }
                else:
                    analysis = analyze_drone(size, battery, style, prop_result, weight)
                    # make sure analysis is a dict
                    if not isinstance(analysis, dict):
                        analysis = {'result': str(analysis)}
                    analysis['prop_result'] = prop_result

            except Exception as e_inner:
                # analysis engine failed: log and provide friendly message
                logger.exception("analyze_drone failed")
                errors.append("การวิเคราะห์ล้มเหลว (internal). โปรดลองใหม่หรือเช็คข้อมูล")
                # still show prop_result to user
                analysis = {'prop_result': prop_result}

        except ValueError as ve:
            logger.warning("Validation error: %s", ve)
            errors.append(str(ve))
        except Exception as e:
            logger.exception("Unexpected error processing POST")
            errors.append("มีข้อผิดพลาดภายในระบบ กรุณาลองใหม่")

    # normalize analysis to prevent template errors
    analysis = safe_analysis(analysis)

    # prefer 'index.html' (app page) if present
    template_name = 'index.html' if os.path.exists(os.path.join(app.root_path, 'templates', 'index.html')) else None
    if template_name:
        return render_template(template_name, analysis=analysis, errors=errors)
    # fallback: simple html
    return f"<html><body><h3>Analysis</h3><pre>{analysis}</pre><p>Errors: {errors}</p></body></html>"

# ---------- error handlers ----------
@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400, message=str(e)), 400

@app.errorhandler(500)
def server_error(e):
    logger.exception("Server error")
    return render_template('error.html', code=500, message='Internal server error'), 500

# ---------- run ----------
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    # Use PORT if provided by Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
