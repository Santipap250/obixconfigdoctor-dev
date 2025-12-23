def calculate_thrust_weight(motor_load, weight):
    # สมมติแรงขับรวม = motor_load * 1000
    thrust = motor_load * 1000
    ratio = round(thrust/weight, 2)
    return f"{ratio}:1"

def estimate_battery_runtime(weight, battery):
    # สมมติค่า mAh ต่อ kg
    if battery == "4S":
        runtime = round(1500 / weight * 3, 1)  # นาที
    else:
        runtime = round(2200 / weight * 3, 1)
    return f"{runtime} นาที"
