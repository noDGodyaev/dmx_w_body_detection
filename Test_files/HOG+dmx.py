import random

import cv2
import imutils
import argparse
import time
from DMXEnttecPro import Controller

HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def detect(frame):
    bounding_box_cordinates, weights = HOGCV.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.03)

    person = 1
    for x, y, w, h in bounding_box_cordinates:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f'person {person}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        person += 1

    cv2.putText(frame, 'Status : Detecting ', (40, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f'Total Persons : {person - 1}', (40, 70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    cv2.imshow('output', frame)
    return frame, person


def detectByCamera(writer):
    video = cv2.VideoCapture('rtsp://172.18.191.159:554/12')
    count = 0
    print('Detecting people...')
    ch1 = 0
    while True:
        check, frame = video.read()
        if check:
            count += 30
            video.set(1, count)
            frame, person = detect(frame)
            if person == 0:
                ch1 = 0
            if person == 1:
                ch1 = 50
            if person == 2:
                ch1 = 255
            if person == 3:
                ch1 = 150
            if person == 4:
                ch1 = 200
            if person == 5:
                ch1 = 250
            if writer is not None:
                writer.write(frame)
        key = cv2.waitKey(1)
        dmx.set_channel(1, 0)
        dmx.set_channel(2, 0)
        dmx.set_channel(3, ch1)
        dmx.set_channel(4, 0)
        dmx.set_channel(5, 0)
        dmx.set_channel(6, 0)
        dmx.set_channel(7, 226)
        dmx.set_channel(8, 255)

        dmx.submit()  # Sends the update to the controller
        if key == ord('q'):
            break
        time.sleep(1)
    video.release()
    cv2.destroyAllWindows()


def detectByPathVideo(path, writer):
    video = cv2.VideoCapture(path)
    check, frame = video.read()
    if not check:
        print('Video Not Found. Please Enter a Valid Path (Full path of Video Should be Provided).')
        return
    print('Detecting people...')
    while video.isOpened():
        # check is True if reading was successful
        check, frame = video.read()
        ch1 = 0
        if check:
            frame = imutils.resize(frame, width=min(800, frame.shape[1]))
            frame, person = detect(frame)
            if person == 1:
                ch1 = 50
            if person == 2:
                ch1 = 100
            if person == 3:
                ch1 = 150
            if person == 4:
                ch1 = 200
            if person == 5:
                ch1 = 250

            if writer is not None:
                writer.write(frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            dmx.set_channel(1, ch1)
            dmx.set_channel(2, 0)
            dmx.set_channel(3, 141)
            dmx.set_channel(4, 0)
            dmx.set_channel(5, 0)
            dmx.set_channel(6, 0)
            dmx.set_channel(7, 226)
            dmx.set_channel(8, 255)
            dmx.get_channel(1)  # Sets DMX channel 1 to max 255

            dmx.submit()  # Sends the update to the controller
        else:
            break
    video.release()
    cv2.destroyAllWindows()


def detectByPathImage(path, output_path):
    image = cv2.imread(path)

    image = imutils.resize(image, width=min(800, image.shape[1]))

    result_image = detect(image)

    if output_path is not None:
        cv2.imwrite(output_path, result_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def argsParser():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-v", "--video", default=None, help="path to Video File ")
    arg_parse.add_argument("-i", "--image", default=None, help="path to Image File ")
    arg_parse.add_argument("-c", "--camera", default=False, help="Set true if you want to use the camera.")
    arg_parse.add_argument("-o", "--output", type=str, help="path to optional output video file")

    return vars(arg_parse.parse_args())


def humanDetector(arrgs):
    image_path = arrgs["image"]
    video_path = arrgs['video']
    if str(arrgs["camera"]) == 'true':
        camera = True
    else:
        camera = False
    writer = None
    if arrgs['output'] is not None and image_path is None:
        writer = cv2.VideoWriter(arrgs['output'], cv2.VideoWriter_fourcc(*'MJPG'), 10, (600, 600))
    if camera:
        print('[INFO] Opening Web Cam.')
        detectByCamera(writer)
    elif video_path is not None:
        print('[INFO] Opening Video from path.')
        detectByPathVideo(video_path, writer)
    elif image_path is not None:
        print('[INFO] Opening Image from path.')
        detectByPathImage(image_path, args['output'])


if __name__ == "__main__":
    dmx = Controller('/dev/ttyUSB0')  # Typical of Linux
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    args = argsParser()
    humanDetector(args)
    dmx.set_channel(1, 255)
    dmx.set_channel(2, 0)
    dmx.set_channel(3, 141)
    dmx.set_channel(4, 0)
    dmx.set_channel(5, 0)
    dmx.set_channel(6, 0)
    dmx.set_channel(7, 226)
    dmx.set_channel(8, 255)
    dmx.get_channel(1)  # Sets DMX channel 1 to max 255

    dmx.submit()  # Sends the update to the controller