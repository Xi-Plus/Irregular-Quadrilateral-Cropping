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


def resize_img_to_show(name, img_temp, small=False):
    if img_temp is None:
        return
    height = img_temp.shape[0]
    width = img_temp.shape[1]
    if small and width <= 900:
        ratio = 1
    else:
        ratio = 900 / width
    height = int(height * ratio)
    width = int(width * ratio)
    cv2.imshow(name, cv2.resize(img_temp, (width, height)))


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


ROW = 0
tk.Button(root, text='Open File', command=openFile).grid(row=ROW, column=0, columnspan=2, sticky='W')

ROW += 1
tk.Label(root, text='TL0').grid(row=ROW, column=0)
tk.Entry(root, textvariable=pos['TL'][0]).grid(row=ROW, column=1)
tk.Button(root, text=' - ', command=changePos('TL', 0, -1)).grid(row=ROW, column=2)
tk.Button(root, text=' + ', command=changePos('TL', 0, +1)).grid(row=ROW, column=3)

tk.Label(root, text=' ').grid(row=ROW, column=4)
tk.Label(root, text='TR0').grid(row=ROW, column=5)
tk.Entry(root, textvariable=pos['TR'][0]).grid(row=ROW, column=6)
tk.Button(root, text=' - ', command=changePos('TR', 0, -1)).grid(row=ROW, column=7)
tk.Button(root, text=' + ', command=changePos('TR', 0, +1)).grid(row=ROW, column=8)

ROW += 1
tk.Label(root, text='TL1').grid(row=ROW, column=0)
tk.Entry(root, textvariable=pos['TL'][1]).grid(row=ROW, column=1)
tk.Button(root, text=' - ', command=changePos('TL', 1, -1)).grid(row=ROW, column=2)
tk.Button(root, text=' + ', command=changePos('TL', 1, +1)).grid(row=ROW, column=3)

tk.Label(root, text=' ').grid(row=ROW, column=4)
tk.Label(root, text='TR1').grid(row=ROW, column=5)
tk.Entry(root, textvariable=pos['TR'][1]).grid(row=ROW, column=6)
tk.Button(root, text=' - ', command=changePos('TR', 1, -1)).grid(row=ROW, column=7)
tk.Button(root, text=' + ', command=changePos('TR', 1, +1)).grid(row=ROW, column=8)

ROW += 1
tk.Label(root, text='').grid(row=ROW, column=0)

ROW += 1
tk.Label(root, text='BL0').grid(row=ROW, column=0)
tk.Entry(root, textvariable=pos['BL'][0]).grid(row=ROW, column=1)
tk.Button(root, text=' - ', command=changePos('BL', 0, -1)).grid(row=ROW, column=2)
tk.Button(root, text=' + ', command=changePos('BL', 0, +1)).grid(row=ROW, column=3)

tk.Label(root, text=' ').grid(row=ROW, column=4)
tk.Label(root, text='BR0').grid(row=ROW, column=5)
tk.Entry(root, textvariable=pos['BR'][0]).grid(row=ROW, column=6)
tk.Button(root, text=' - ', command=changePos('BR', 0, -1)).grid(row=ROW, column=7)
tk.Button(root, text=' + ', command=changePos('BR', 0, +1)).grid(row=ROW, column=8)

ROW += 1
tk.Label(root, text='BL1').grid(row=ROW, column=0)
tk.Entry(root, textvariable=pos['BL'][1]).grid(row=ROW, column=1)
tk.Button(root, text=' - ', command=changePos('BL', 1, -1)).grid(row=ROW, column=2)
tk.Button(root, text=' + ', command=changePos('BL', 1, +1)).grid(row=ROW, column=3)

tk.Label(root, text=' ').grid(row=ROW, column=4)
tk.Label(root, text='BR1').grid(row=ROW, column=5)
tk.Entry(root, textvariable=pos['BR'][1]).grid(row=ROW, column=6)
tk.Button(root, text=' - ', command=changePos('BR', 1, -1)).grid(row=ROW, column=7)
tk.Button(root, text=' + ', command=changePos('BR', 1, +1)).grid(row=ROW, column=8)

ROW += 1
tk.Label(root, text='').grid(row=ROW, column=0)

ROW += 1
tk.Label(root, text='Out0').grid(row=ROW, column=0)
tk.Entry(root, textvariable=output[0]).grid(row=ROW, column=1)
tk.Button(root, text=' - ', command=changeOutput(0, -1)).grid(row=ROW, column=2)
tk.Button(root, text=' + ', command=changeOutput(0, +1)).grid(row=ROW, column=3)

tk.Label(root, text=' ').grid(row=ROW, column=4)
tk.Label(root, text='Out1').grid(row=ROW, column=5)
tk.Entry(root, textvariable=output[1]).grid(row=ROW, column=6)
tk.Button(root, text=' - ', command=changeOutput(1, -1)).grid(row=ROW, column=7)
tk.Button(root, text=' + ', command=changeOutput(1, +1)).grid(row=ROW, column=8)

ROW += 1
tk.Button(root, text='Save File', command=saveFile).grid(row=ROW, column=0, columnspan=2, sticky='W')

root.mainloop()
