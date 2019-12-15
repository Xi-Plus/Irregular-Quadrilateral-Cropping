import argparse
import os
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np

parser = argparse.ArgumentParser()
# parser.add_argument('source', type=str)
parser.add_argument('--height', type=int, default=450)
parser.add_argument('--width', type=int, default=800)
args = parser.parse_args()
print(args)


root = tk.Tk()
root.title('Irregular Quadrilateral Cropping')

pos = {
    'TL': (tk.IntVar(root, value=0), tk.IntVar(root, value=0)),
    'TR': (tk.IntVar(root, value=0), tk.IntVar(root, value=1600)),
    'BL': (tk.IntVar(root, value=900), tk.IntVar(root, value=0)),
    'BR': (tk.IntVar(root, value=900), tk.IntVar(root, value=1600)),
}
output = (tk.IntVar(root, value=args.height), tk.IntVar(root, value=args.width))

img = None
fileName = None
fileExtension = None
inputRatio = None


def mark_line(img):
    if img is None:
        return
    img_temp = img.copy()
    cv2.line(
        img_temp,
        (pos['TL'][1].get(), pos['TL'][0].get()),
        (pos['TR'][1].get(), pos['TR'][0].get()),
        (0, 0, 255), 2, cv2.LINE_AA
    )
    cv2.line(
        img_temp,
        (pos['BL'][1].get(), pos['BL'][0].get()),
        (pos['BR'][1].get(), pos['BR'][0].get()),
        (0, 0, 255), 2, cv2.LINE_AA
    )
    cv2.line(
        img_temp,
        (pos['TL'][1].get(), pos['TL'][0].get()),
        (pos['BL'][1].get(), pos['BL'][0].get()),
        (0, 0, 255), 2, cv2.LINE_AA
    )
    cv2.line(
        img_temp,
        (pos['TR'][1].get(), pos['TR'][0].get()),
        (pos['BR'][1].get(), pos['BR'][0].get()),
        (0, 0, 255), 2, cv2.LINE_AA
    )
    return img_temp


def crop_image():
    sourcePoints = np.array([
        (pos['TL'][1].get(), pos['TL'][0].get()),
        (pos['TR'][1].get(), pos['TR'][0].get()),
        (pos['BR'][1].get(), pos['BR'][0].get()),
        (pos['BL'][1].get(), pos['BL'][0].get()),
    ], dtype=np.float32)
    dstPoints = np.array([
        [0, 0],
        [output[1].get(), 0],
        [output[1].get(), output[0].get()],
        [0, output[0].get()],
    ], dtype=np.float32)
    M = cv2.getPerspectiveTransform(sourcePoints, dstPoints)
    img_result = cv2.warpPerspective(img, M, (output[1].get(), output[0].get()))
    return img_result


def show_images():
    if img is None:
        return

    resize_img_to_show('input', mark_line(img))
    resize_img_to_show('output', crop_image(), small=True)
    cv2.setMouseCallback('input', mouseClicked)


def resize_img_to_show(name, img_temp, small=False):
    if img_temp is None:
        return
    height = img_temp.shape[0]
    width = img_temp.shape[1]
    if small and height <= 700:
        ratio = 1
    else:
        ratio = 700 / height
    height = int(height * ratio)
    width = int(width * ratio)
    cv2.imshow(name, cv2.resize(img_temp, (width, height)))

    if name == 'input':
        global inputRatio
        inputRatio = ratio


def openFile():
    global img, fileName, fileExtension
    file_path = filedialog.askopenfilename()
    print(file_path)
    if file_path is not None:
        fileName = os.path.basename(file_path)
        fileExtension = os.path.splitext(file_path)[1]

        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        pos['BL'][0].set(img.shape[0] - 1)
        pos['BR'][0].set(img.shape[0] - 1)
        pos['TR'][1].set(img.shape[1] - 1)
        pos['BR'][1].set(img.shape[1] - 1)
        show_images()


def saveFile():
    global img
    if img is None:
        return
    out_path = filedialog.asksaveasfilename(
        filetypes=[
            ('PNG File', '*.png'),
            ('JPEG File', '*.jpg'),
            ('All files', '*'),
        ],
        initialfile=fileName,
        defaultextension=fileExtension,
    )
    print(out_path)
    if out_path:
        img_result = crop_image()
        cv2.imwrite(out_path, img_result)


def changePos(corner, xy, diff):
    def wrapper():
        pos[corner][xy].set(pos[corner][xy].get() + diff)
        show_images()
    return wrapper


def changeOutput(xy, diff):
    def wrapper():
        output[xy].set(output[xy].get() + diff)
        show_images()
    return wrapper


def mouseClicked(event, p1, p0, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON)):
        p0 = int(p0 / inputRatio)
        p1 = int(p1 / inputRatio)

        print(p0, p1)
        minDis = 1e9
        minCorner = None
        for corner in pos:
            tempDis = (pos[corner][0].get() - p0)**2 + (pos[corner][1].get() - p1)**2
            if tempDis < minDis:
                minDis = tempDis
                minCorner = corner

        pos[minCorner][0].set(p0)
        pos[minCorner][1].set(p1)
        show_images()


ROW = 0
tk.Button(root, text='Open File', command=openFile).grid(row=ROW, column=0, columnspan=2, sticky='W')

for xy in [0, 1]:
    ROW += 1
    COL = -1
    for corner in ['TL', 'TR']:
        COL += 1
        tk.Label(root, text='{}{}'.format(corner, xy)).grid(row=ROW, column=COL)
        COL += 1
        tk.Entry(root, textvariable=pos[corner][xy]).grid(row=ROW, column=COL)
        for diff in [1, 10, 100]:
            COL += 1
            tk.Button(root, text=' {:+d} '.format(-diff), command=changePos(corner, xy, -diff)).grid(row=ROW, column=COL)
            COL += 1
            tk.Button(root, text=' {:+d} '.format(+diff), command=changePos(corner, xy, +diff)).grid(row=ROW, column=COL)

ROW += 1
tk.Label(root, text='').grid(row=ROW, column=0)

for xy in [0, 1]:
    ROW += 1
    COL = -1
    for corner in ['BL', 'BR']:
        COL += 1
        tk.Label(root, text='{}{}'.format(corner, xy)).grid(row=ROW, column=COL)
        COL += 1
        tk.Entry(root, textvariable=pos[corner][xy]).grid(row=ROW, column=COL)
        for diff in [1, 10, 100]:
            COL += 1
            tk.Button(root, text=' {:+d} '.format(-diff), command=changePos(corner, xy, -diff)).grid(row=ROW, column=COL)
            COL += 1
            tk.Button(root, text=' {:+d} '.format(+diff), command=changePos(corner, xy, +diff)).grid(row=ROW, column=COL)

ROW += 1
tk.Label(root, text='').grid(row=ROW, column=0)

ROW += 1
COL = -1
for xy in [0, 1]:
    COL += 1
    tk.Label(root, text='Out{}'.format(xy)).grid(row=ROW, column=COL)
    COL += 1
    tk.Entry(root, textvariable=output[xy]).grid(row=ROW, column=COL)
    for diff in [1, 10, 100]:
        COL += 1
        tk.Button(root, text=' {:+d} '.format(-diff), command=changeOutput(xy, -diff)).grid(row=ROW, column=COL)
        COL += 1
        tk.Button(root, text=' {:+d} '.format(+diff), command=changeOutput(xy, +diff)).grid(row=ROW, column=COL)

ROW += 1
tk.Button(root, text='Save File', command=saveFile).grid(row=ROW, column=0, columnspan=2, sticky='W')

root.mainloop()
