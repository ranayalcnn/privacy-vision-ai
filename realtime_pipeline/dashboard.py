import cv2
import math
import time


# OpenCV colors are BGR. The palette deliberately stays cool and neutral so
# the camera feed remains the focus while status colors stay easy to scan.
PANEL_BG = (24, 27, 30)
PANEL_BORDER = (68, 72, 75)
TEXT_PRIMARY = (240, 238, 234)
TEXT_SECONDARY = (174, 177, 176)
SUCCESS = (126, 207, 105)
DANGER = (92, 92, 238)
CHIP_BG = (38, 42, 45)
HAND_GLOW = (196, 164, 54)
HAND_CORE = (225, 204, 112)


def rounded_box(frame, box, color):
    x1, y1, x2, y2 = box
    radius = 12

    cv2.line(
        frame,
        (x1 + radius, y1),
        (x2 - radius, y1),
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.line(
        frame,
        (x1 + radius, y2),
        (x2 - radius, y2),
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.line(
        frame,
        (x1, y1 + radius),
        (x1, y2 - radius),
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.line(
        frame,
        (x2, y1 + radius),
        (x2, y2 - radius),
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.ellipse(
        frame,
        (x1 + radius, y1 + radius),
        (radius, radius),
        180,
        0,
        90,
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.ellipse(
        frame,
        (x2 - radius, y1 + radius),
        (radius, radius),
        270,
        0,
        90,
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.ellipse(
        frame,
        (x1 + radius, y2 - radius),
        (radius, radius),
        90,
        0,
        90,
        color,
        2,
        cv2.LINE_AA,
    )

    cv2.ellipse(
        frame,
        (x2 - radius, y2 - radius),
        (radius, radius),
        0,
        0,
        90,
        color,
        2,
        cv2.LINE_AA,
    )


def draw_hand_effect(frame, app):
    points = getattr(app, "hand_points", [])

    if not points:
        return

    pulse = int(
        2 + abs(math.sin(time.perf_counter() * 5)) * 2
    )

    glow = frame.copy()

    for point in points:
        cv2.circle(
            glow,
            point,
            10 + pulse,
            HAND_GLOW,
            -1,
            cv2.LINE_AA,
        )

    frame[:] = cv2.addWeighted(
        glow,
        0.16,
        frame,
        0.84,
        0,
    )

    fingertip_indexes = [4, 8, 12, 16, 20]

    for index, point in enumerate(points):
        radius = 4 if index in fingertip_indexes else 2

        cv2.circle(
            frame,
            point,
            radius + pulse // 2,
            TEXT_PRIMARY,
            -1,
            cv2.LINE_AA,
        )

        cv2.circle(
            frame,
            point,
            radius,
            HAND_CORE,
            -1,
            cv2.LINE_AA,
        )


def draw_dashboard(frame, app, fps):
    h, w = frame.shape[:2]
    mode_color = app.mode_manager.get_color()
    status = "ACTIVE" if app.privacy_enabled else "OFF"
    status_color = (
        SUCCESS
        if app.privacy_enabled
        else DANGER
    )

    # A compact HUD keeps almost the entire camera image unobstructed.
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w - 10, 55), PANEL_BG, -1)
    frame[:] = cv2.addWeighted(overlay, 0.82, frame, 0.18, 0)

    cv2.rectangle(
        frame, (10, 10), (w - 10, 55), PANEL_BORDER, 1, cv2.LINE_AA
    )
    cv2.rectangle(frame, (10, 10), (15, 55), mode_color, -1)

    cv2.circle(
        frame,
        (29, 32),
        5,
        status_color,
        -1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        status,
        (41, 37),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        status_color,
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        app.mode_manager.mode,
        (112, 37),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        mode_color,
        1,
        cv2.LINE_AA,
    )

    right_text = f"{len(app.face_boxes)} FACE  |  {fps:.0f} FPS"
    text_size, _ = cv2.getTextSize(
        right_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1
    )
    cv2.putText(
        frame,
        right_text,
        (w - text_size[0] - 25, 37),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        TEXT_SECONDARY,
        1,
        cv2.LINE_AA,
    )

    if app.privacy_enabled:
        for box in app.face_boxes:
            rounded_box(frame, box, mode_color)

    draw_hand_effect(frame, app)

    if not app.privacy_enabled:
        cv2.rectangle(
            frame,
            (4, 4),
            (w - 5, h - 5),
            DANGER,
            2,
            cv2.LINE_AA,
        )

    if time.perf_counter() < app.notification_until:
        text = app.notification_text

        size, _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            2,
        )

        box_w = size[0] + 35
        box_h = 45
        x1 = (w - box_w) // 2
        y1 = h - 65

        cv2.rectangle(
            frame,
            (x1, y1),
            (x1 + box_w, y1 + box_h),
            PANEL_BG,
            -1,
            cv2.LINE_AA,
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x1 + box_w, y1 + box_h),
            mode_color,
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            text,
            (x1 + 17, y1 + 29),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            mode_color,
            2,
            cv2.LINE_AA,
        )

    return frame
