import cv2
import numpy as np
import math

# ==========================
# Kalibrasi Pixel ke mm
# ==========================
# Ganti nilai ini sesuai hasil kalibrasi Anda
# Contoh: objek 100 mm terlihat 200 pixel → scale_x = 100/200 = 0.5
scale_x = 0.5  # mm per pixel untuk sumbu X (horizontal)
scale_y = 0.5  # mm per pixel untuk sumbu Y (vertikal)

# Buka kamera
cap = cv2.VideoCapture(1)

x_kiri, y_kiri, w_kiri, h_kiri = 0, 0, 0, 0
x_kanan, y_kanan, w_kanan, h_kanan = 0, 0, 0, 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Ubah ke grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)

    # Cari kontur
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Titik tengah frame
    frame_center_x = frame.shape[1] // 2
    frame_center_y = frame.shape[0] // 2
    cv2.circle(frame, (frame_center_x, frame_center_y), 5, (255, 0, 0), -1)

    objek_kiri = None
    objek_kanan = None

    for cnt in contours:
        if cv2.contourArea(cnt) > 1000:
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            # Perbaikan angle agar sesuai tegak lurus
            if w < h:
                angle = angle + 90
            angle = int(angle)

            # Kotak objek
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

            # Simpan objek kiri / kanan
            if x < frame_center_x:
                objek_kiri = (int(x), int(y), int(w), int(h), angle)
                cv2.putText(frame, "Objek 1", (int(x) - 40, int(y) - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                objek_kanan = (int(x), int(y), int(w), int(h), angle)
                cv2.putText(frame, "Objek 2", (int(x) - 40, int(y) - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Tampilkan data masing-masing objek
    if objek_kiri:
        x, y, w, h, angle = objek_kiri

        # Konversi ke mm
        x_mm = x * scale_x
        y_mm = y * scale_y
        w_mm = w * scale_x
        h_mm = h * scale_y

        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"Angle: {angle} deg", (x - 60, y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"W:{w_mm:.2f}mm H:{h_mm:.2f}mm", (x - 60, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        x_kiri, y_kiri = x_mm, y_mm
        w_kiri, h_kiri = w_mm, h_mm

    if objek_kanan:
        x, y, w, h, angle = objek_kanan

        # Konversi ke mm
        x_mm = x * scale_x
        y_mm = y * scale_y
        w_mm = w * scale_x
        h_mm = h * scale_y

        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"Angle: {angle} deg", (x - 60, y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"W:{w_mm:.2f}mm H:{h_mm:.2f}mm", (x - 60, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        x_kanan, y_kanan = x_mm, y_mm
        w_kanan, h_kanan = w_mm, h_mm

    # Hitung jarak antar objek (dalam mm)
    if objek_kiri and objek_kanan:
        x1, y1, _, _, _ = objek_kiri
        x2, y2, _, _, _ = objek_kanan

        x1_mm = x1 * scale_x
        y1_mm = y1 * scale_y
        x2_mm = x2 * scale_x
        y2_mm = y2 * scale_y

        jarak = math.sqrt((x2_mm - x1_mm) ** 2 + (y2_mm - y1_mm) ** 2)
        cv2.putText(frame, f"Jarak Objek1-Objek2: {jarak:.2f}mm", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Tampilkan hasil
    cv2.imshow("Deteksi Blok", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Print hasil di terminal
    print("Kanan : X=", x_kanan, "mm  Y=", y_kanan, "mm  W=", w_kanan, "mm  H=", h_kanan, "mm")
    print("Kiri  : X=", x_kiri, "mm  Y=", y_kiri, "mm  W=", w_kiri, "mm  H=", h_kiri, "mm")

cap.release()
cv2.destroyAllWindows()
