import cv2
import numpy as np
import pandas as pd
import argparse
import os

# Argument parser to allow image path as a command-line argument
ap = argparse.ArgumentParser()
args = vars(ap.parse_args())
img_path = "D:/Color_detection/scenery.jpg"

# Check if the provided image path exists
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image file not found at {img_path}")

# Load the image using OpenCV
img = cv2.imread(img_path)

# Resize image if it's too large
scale_percent = 40  # Resize to 60% of original size
if img.shape[0] > 800 or img.shape[1] > 1200:  # If height or width is too large
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (width, height))

# Declare global variables
clicked = False
r = g = b = xpos = ypos = 0

# Load colors CSV file
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('D:/Color_detection/colors.csv', names=index, header=None)

# To store color history
color_history = []

# Function to calculate closest color
def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    hex_color = csv.loc[csv['color_name'] == cname, 'hex'].values[0]
    return cname, hex_color

# Function to handle double-click event
def draw_function(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)
        
        # Add color to history
        color_name, hex_color = getColorName(r, g, b)
        color_history.append((color_name, hex_color, r, g, b))

# Setup OpenCV window
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

# Display color history in a separate window
def show_color_history():
    history_img = np.zeros((200, 300, 3), dtype=np.uint8)
    y_offset = 10
    for color in color_history[-5:]:  # Display last 5 colors
        color_name, hex_color, r, g, b = color
        cv2.rectangle(history_img, (10, y_offset), (290, y_offset + 30), (b, g, r), -1)
        cv2.putText(history_img, f"{color_name} Hex={hex_color} R={r} G={g} B={b}", (15, y_offset + 20), 1, 0.7, (255, 255, 255), 1)
        y_offset += 40
    cv2.imshow("Color History", history_img)

# Save color history to CSV file
def save_color_history():
    df = pd.DataFrame(color_history, columns=["Color Name", "Hex", "R", "G", "B"])
    df.to_csv("color_history.csv", index=False)
    print("Color history saved to color_history.csv")

while True:
    cv2.imshow("image", img)
    show_color_history()
    if clicked:
        # Display rectangle with color name and RGB values
        cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)
        color_name, hex_color = getColorName(r, g, b)
        text = f"{color_name} Hex={hex_color} R={r} G={g} B={b}"
        
        # Show text in white or black based on brightness
        text_color = (255, 255, 255) if (r + g + b < 600) else (0, 0, 0)
        cv2.putText(img, text, (50, 50), 2, 0.8, text_color, 2, cv2.LINE_AA)
        
        clicked = False
    
    # Press 's' to save color history, 'esc' to exit
    key = cv2.waitKey(20)
    if key == 27:  # Esc key
        break
    elif key == ord('s'):
        save_color_history()
cv2.destroyAllWindows()
