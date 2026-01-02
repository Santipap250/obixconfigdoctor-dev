def analyze_propeller(prop_size, prop_pitch, blade_count, style):
    """
    คืนค่าเป็น dict:
    {
      "summary": "...",
      "effect": {
         "noise": int (0..10),
         "motor_load": int (0..10),
         "efficiency": "string",
         "grip": "string"
      },
      "recommendation": "..."
    }
    """
    result = {}

    # normalize
    prop_size = float(prop_size)
    prop_pitch = float(prop_pitch)
    blade_count = int(blade_count)

    # baseline scores
    noise_score = 0
    motor_load = 0
    efficiency = "กลาง"

    # Pitch effect
    if prop_pitch >= 4.5:
        noise_score += 3
        motor_load += 3
        efficiency = "แรง (กินไฟ)"
    elif prop_pitch >= 4.0:
        noise_score += 2
        motor_load += 2
        efficiency = "สมดุล"
    else:
        noise_score += 1
        motor_load += 1
        efficiency = "ประหยัด / นุ่ม"

    # Blade count effect
    if blade_count >= 4:
        noise_score += 3
        motor_load += 3
        grip = "หนึบมาก"
    elif blade_count == 3:
        noise_score += 2
        motor_load += 2
        grip = "หนึบดี"
    else:
        noise_score += 1
        motor_load += 1
        grip = "นุ่ม ลอย"

    # Size tweak (bigger props => more motor load in many cases)
    if prop_size >= 6:
        motor_load += 2
    elif prop_size >= 5:
        motor_load += 1

    # Clamp scores to 0..10
    noise_score = max(0, min(10, noise_score))
    motor_load = max(0, min(10, motor_load))

    # Style recommendation text
    if style == "racing":
        recommend = "เหมาะกับ Racing — ตอบสนองไว แต่ต้องเช็กความร้อนและใช้ใบพัดเบากว่า"
    elif style == "longrange":
        recommend = "เหมาะกับ Long Range — ประหยัดไฟ ควบคุมง่าย แต่เลือกใบพัด Pitch ต่ำ/กลาง"
    else:  # freestyle / default
        recommend = "เหมาะกับ Freestyle — สมดุล ระหว่างแรงกับการควบคุม"

    # Summary string
    result["summary"] = f"{prop_size:.1f}\" × {blade_count} ใบ (Pitch {prop_pitch:.1f}) — {grip}, {efficiency}"
    result["effect"] = {
        "noise": noise_score,
        "motor_load": motor_load,
        "efficiency": efficiency,
        "grip": grip
    }
    result["recommendation"] = recommend

    return result