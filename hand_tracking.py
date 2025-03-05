import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import os

# สร้างโฟลเดอร์ถ้ายังไม่มี
folder_name = "captured_images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# เปิดกล้อง
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# รายชื่อนิ้ว
fingerNames = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

# ตั้งค่าหน้าต่างเป็น Fullscreen
cv2.namedWindow("Hand Tracking", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Hand Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ตัวแปรเพื่อจับเวลา
countdown_time = 3  # เวลานับถอยหลัง 3 วินาที
countdown_started = False
start_time = 0
image_captured = False
waiting_for_hand = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hands, frame = detector.findHands(frame)

    if hands:
        y_position = 30 
        for hand in hands:
            handType = hand["type"]  # ซ้ายหรือขวา
            fingers = detector.fingersUp(hand)  # ตรวจสอบนิ้วที่ยกขึ้น
            fingerCount = fingers.count(1)  # นับนิ้วที่ยกขึ้น

            # รายชื่อนิ้วที่ถูกยกขึ้น
            raisedFingers = [fingerNames[i] for i in range(5) if fingers[i] == 1]
            raisedFingersText = ", ".join(raisedFingers) if raisedFingers else "None"

            # แสดงข้อมูล (ปรับให้เล็กลง)
            cv2.putText(frame, f'{handType} Hand - Fingers: {fingerCount}', (20, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_position += 25
            cv2.putText(frame, f'Raised: {raisedFingersText}', (20, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_position += 25  # ขยับลงเพื่อไม่ให้ข้อความทับกัน

            # เช็คว่ามือขวายกเฉพาะนิ้วชี้และนิ้วกลาง
            if handType == "Right" and fingers[1] == 1 and fingers[2] == 1 and all(f == 0 for f in [fingers[0], fingers[3], fingers[4]]):
                if not countdown_started:  # ถ้ายังไม่เริ่มจับเวลา
                    countdown_started = True
                    start_time = time.time()  # เริ่มจับเวลา

                # คำนวณเวลานับถอยหลัง
                elapsed_time = time.time() - start_time
                remaining_time = countdown_time - int(elapsed_time)

                # ตำแหน่งกลางจอ
                h, w, _ = frame.shape
                center_x, center_y = w // 2, h // 2

                # ขนาดข้อความที่จะแสดง
                text = f"Capturing in {remaining_time}s"
                (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
                
                # คำนวณตำแหน่ง X และ Y เพื่อให้ข้อความอยู่กลางจอ
                x = center_x - text_width // 2
                y = center_y - text_height // 2

                # แสดงข้อความเวลานับถอยหลังกลางจอ (สีขาว)
                if remaining_time > 0:
                    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                elif remaining_time <= 0 and not image_captured:  # เมื่อเวลาหมดแล้วและยังไม่ได้จับภาพ
                    # บันทึกภาพ
                    img_name = f"{folder_name}/captured_image_{int(time.time())}.png"
                    cv2.imwrite(img_name, frame)
                    print(f"Image saved as {img_name}")
                    image_captured = True  # ตั้งค่าสถานะให้จับภาพแล้ว
                    countdown_started = False  # รีเซ็ตการจับเวลา
                    time.sleep(1)  # ให้เวลา 1 วินาที ก่อนกลับสู่โหมดรอการยกนิ้วใหม่

                # รีเซ็ตเมื่อจับภาพเสร็จ
                if image_captured:
                    image_captured = False  # รีเซ็ตสถานะเพื่อให้จับภาพใหม่ได้

    # รีเซ็ตสถานะเมื่อไม่มีมืออยู่ในจอ
    if not hands and countdown_started and not image_captured:
        elapsed_time = time.time() - start_time
        remaining_time = countdown_time - int(elapsed_time)

        # ตำแหน่งกลางจอ
        h, w, _ = frame.shape
        center_x, center_y = w // 2, h // 2

        # ขนาดข้อความที่จะแสดง
        text = f"Capturing in {remaining_time}s"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
        
        # คำนวณตำแหน่ง X และ Y เพื่อให้ข้อความอยู่กลางจอ
        x = center_x - text_width // 2
        y = center_y - text_height // 2

        # แสดงข้อความเวลานับถอยหลังกลางจอ (สีขาว)
        if remaining_time > 0:
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        elif remaining_time <= 0 and not image_captured:  # เมื่อเวลาหมดแล้วและยังไม่ได้จับภาพ
            # บันทึกภาพ
            img_name = f"{folder_name}/captured_image_{int(time.time())}.png"
            cv2.imwrite(img_name, frame)
            print(f"Image saved as {img_name}")
            image_captured = True  # ตั้งค่าสถานะให้จับภาพแล้ว
            countdown_started = False  # รีเซ็ตการจับเวลา

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # กด 'q' เพื่อปิดโปรแกรม
        break

cap.release()
cv2.destroyAllWindows()
