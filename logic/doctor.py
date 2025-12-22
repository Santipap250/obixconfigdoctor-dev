def analyze(cli):
    if not cli:
        return "❌ ยังไม่ได้วาง CLI"

    issues = []

    if "gyro_lowpass2_hz = 0" in cli:
        issues.append("⚠️ ปิด Gyro LPF2 เสี่ยงสั่น")

    if "throttle_limit_percent = 100" in cli:
        issues.append("ℹ️ Throttle 100% กินแบต")

    if not issues:
        return "✅ ค่าโดยรวมดูโอเค"

    return "\n".join(issues)
