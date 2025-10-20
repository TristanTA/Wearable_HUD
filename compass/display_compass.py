import cv2

LIMA = (85, 191, 36)

def draw_cardinal_direction(frame, world_angle, tick):
    if world_angle == 0:
        label = "N"
    elif world_angle == 90:
        label = "E"
    elif world_angle == 180:
        label = "S"
    elif world_angle == 270:
        label = "W"
    else:
        return
    text_x = tick[0][0] - 8
    text_y = tick[0][1] - 12
    cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, LIMA, 2)


def show_compass(frame, heading):
    # Compass baground
    overlay = frame.copy()
    height, width, channels = frame.shape
    top_left = (int((width * 0.25)), int((height * 0.85)))
    bottom_right = (int((width * 0.75)), int((height * 0.95)))
    cv2.rectangle(overlay, top_left, bottom_right, LIMA, -1)
    alpha = 0.4
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Ticks and Text
    top_y = int(height * 0.88)
    bottom_y = int(height * 0.92)
    center_compass_x = int(width / 2)
    visible_arc = 90
    compass_band_width = bottom_right[0] - top_left[0]
    pixels_per_degree = compass_band_width / visible_arc
    for world_angle in range(0, 360, 5):
        offset = (world_angle - heading + 540) % 360 - 180
        if abs(offset) <= visible_arc / 2:
            x = int(center_compass_x + offset * pixels_per_degree)
            cv2.line(frame, (x, top_y), (x, bottom_y), LIMA, 2)
            if world_angle in (0, 90, 180, 270):
                draw_cardinal_direction(frame, world_angle, tick=((x, top_y), (x, bottom_y)))
            