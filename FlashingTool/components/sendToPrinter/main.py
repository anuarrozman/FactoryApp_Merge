#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import segno
import os
import subprocess
import sys

######## GLOBAL CONFIGURATION ########

CONFIG_FONT = "CSADigits-Regular.ttf"  # Font file, Default = "CSADigits-Regular.ttf", please place it inside Files folder.
CONFIG_DPI = 300 # DPI of the template image, Default = 300 (Standard for printing).
CONFIG_MM_TO_POINTS_RATIO = 2.83465  # 1 mm = 2.83465 points.
CONFIG_PDF_MARGIN_MM = 5  # PDF Margin in mm, Default = 5.
CONFIG_PRINTER_TIMEOUT = 7 # Seconds it take to send data to printer before printing the next one, Default = 7.

###### TEXT DESIGN CONFIGURATION ######

TXT_TEMPLATE = "text_template.png"  # Template file name, Default = "text_template.png", please place it inside Files folder.
TXT_TEXT_FONT_SIZE = 24  # Font size in pixels, Default = 24.
TXT_TEXT_Y_OFFSET = 0  # Text Y placement offset, Higher = Text Y placement will be lower, Lower = Text Y placement will be higher, Default = 0.
TXT_TEXT_X_OFFSET = 50  # Text X placement offset, Higher = Text X placement will be more to the left, Lower = Text X placement will be more to the right, Default = 50.

TXT_PDF_WIDTH_MM = 16  # Width of the generated pdf in mm, Default = 16.
TXT_PDF_HEIGHT_MM = 10  # Height of the generated pdf in mm, Default = 10.

TXT_OUTPUT_PNG = "text_result.png"  # PNG output file name, Default = "text_result.png".
TXT_OUTPUT_PDF = "text_result.pdf"  # PDF output file name, Default = "text_result.pdf".

####### QR DESIGN CONFIGURATION #######

QR_TEMPLATE = "qr_template.png"  # Template file name, please place it inside Files folder, Default = "qr_template.png". 
QR_SCALE_FACTOR = 28.5 # QR Scale Factor, Higher = QR code will be scaled smaller, Lower = QR code will be scaled bigger, Default = 28.5.
QR_X_OFFSET = 0  # Text X placement offset, Higher = Text X placement offset will be more to the left, Lower = Text X offset will be more to the right, Default = 0.
QR_Y_OFFSET = 12.5  # QR Y placement offset, Higher = QR Y placement offset will be lower, Lower = QR Y offset will be higher, Default = 12.5.

QR_TEXT_FONT_SIZE = 96  # Higher = Font size will be bigger, Lower = Font size will be smaller, Default = 96.
QR_TEXT_X_OFFSET = 0 # Text X placement offset, Higher = Text X placement will be more to the left, Lower = Text X placement will be more to the right, Default = 0.
QR_TEXT_Y_OFFSET = 167  # Text Y placement offset, # Smaller = Text Y placement will be lower, Higher = Text Y placement will be higher, Default = 167.

QR_PDF_WIDTH_MM = 22  # Width of the generated pdf in mm, Default = 22.
QR_PDF_HEIGHT_MM = 31  # Height of the generated pdf in mm, Default = 31.

QR_OUTPUT_PNG = "qr_result.png"  # PNG output file name, Default = "qr_result.png".
QR_OUTPUT_PDF = "qr_result.pdf"  # PDF output file name, Default = "qr_result.pdf".

####### POLYAIRE DESIGN CONFIGURATION #######

POLYAIRE_TEMPLATE = "polyaire_template.png"  # Template file name, please place it inside Files folder, Default = "polyaire_template.png"
POLYAIRE_SCALE_FACTOR = 4.55 # QR Scale Factor, Higher = QR code will be scaled smaller, Lower = QR code will be scaled bigger, Default = 4.55
POLYAIRE_X_OFFSET = 110  # Text X placement offset, Higher = Text X placement offset will be more to the left, Lower = Text X offset will be more to the right, Default = 110
POLYAIRE_Y_OFFSET = -1 # QR Y placement offset, Higher = QR Y placement offset will be lower, Lower = QR Y offset will be higher, Default = -1

POLYAIRE_TEXT_FONT_SIZE = 25  # Higher = Font size will be bigger, Lower = Font size will be smaller, Default = 25
POLYAIRE_TEXT_X_OFFSET = -65 # Text X placement offset, Higher = Text X placement will be more to the left, Lower = Text X placement will be more to the right, Default = -65
POLYAIRE_TEXT_Y_OFFSET = 62.5  # Text Y placement offset, # Smaller = Text Y placement will be lower, Higher = Text Y placement will be higher, Default = 62.5

POLYAIRE_PDF_WIDTH_MM = 31  # Width of the generated pdf in mm, Default = 31
POLYAIRE_PDF_HEIGHT_MM = 12  # Height of the generated pdf in mm, Default = 12

POLYAIRE_OUTPUT_PNG = "polyaire_result.png"  # PNG output file name, Default = "polyaire_result.png".
POLYAIRE_OUTPUT_PDF = "polyaire_result.pdf"  # PDF output file name, Default = "polyaire_result.pdf".

# Update the current working directory to the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Convert mm to points
def mm_to_points(mm):
    return mm * CONFIG_MM_TO_POINTS_RATIO

def send_to_printer(file_path, printer_ip, printer_port):
    try:
        subprocess.run(["curl", "--data-binary", f"@{file_path}", "http://" + printer_ip + ":" + printer_port], timeout=CONFIG_PRINTER_TIMEOUT)
    except subprocess.TimeoutExpired:
        return

##### Text Design Dimensions #####
# Convert desired dimensions and margin to points
text_width_pt = mm_to_points(TXT_PDF_WIDTH_MM)
text_height_pt = mm_to_points(TXT_PDF_HEIGHT_MM)
text_margin_pt = mm_to_points(CONFIG_PDF_MARGIN_MM)

# Adjusted dimensions for the PDF with margin
text_width_margin_pt = text_width_pt + 2 * text_margin_pt
text_height_margin_pt = text_height_pt + 2 * text_margin_pt

##### QR Design Dimensions #####
# Convert desired dimensions and margin to points
qr_width_pt = mm_to_points(QR_PDF_WIDTH_MM)
qr_height_pt = mm_to_points(QR_PDF_HEIGHT_MM)
qr_margin_pt = mm_to_points(CONFIG_PDF_MARGIN_MM)

# Adjusted dimensions for the PDF with margin
qr_width_margin_pt = qr_width_pt + 2 * qr_margin_pt
qr_height_margin_pt = qr_height_pt + 2 * qr_margin_pt

##### Polyaire Design Dimensions #####
# Convert desired dimensions and margin to points
polyaire_width_pt = mm_to_points(POLYAIRE_PDF_WIDTH_MM)
polyaire_height_pt = mm_to_points(POLYAIRE_PDF_HEIGHT_MM)
polyaire_margin_pt = mm_to_points(CONFIG_PDF_MARGIN_MM)

# Adjusted dimensions for the PDF with margin
polyaire_width_margin_pt = polyaire_width_pt + 2 * polyaire_margin_pt
polyaire_height_margin_pt = polyaire_height_pt + 2 * polyaire_margin_pt

def generate_label_design(number, printer_ip, printer_port):

    num_1 = number[:5]
    num_2 = number[5:9]
    num_3 = number[9:]

    # Label design text format is 
    # "XXXX-
    # XXX-
    # XXX"
    number = num_1 + "\n" + num_2 + "\n" + num_3

    # Open the template image
    template_img = Image.open(os.path.abspath(TXT_TEMPLATE)).convert("RGBA")
    template_w, template_h = template_img.size
    template_dpi = template_img.info.get('dpi', (CONFIG_DPI, CONFIG_DPI))

    # Create a copy of the template image to modify
    output_img = template_img.copy()

    # Prepare to draw the numeric code
    draw = ImageDraw.Draw(output_img)
    font = ImageFont.truetype(CONFIG_FONT, TXT_TEXT_FONT_SIZE)

    # Calculate the position for the numeric code text
    text_x = template_w - TXT_TEXT_X_OFFSET
    text_y = template_h / 2 + TXT_TEXT_Y_OFFSET

    # Draw the numeric code text onto the image
    draw.text((text_x, text_y), number, font=font, fill="black", anchor="mm")

    # Save the final image with the correct CONFIG_DPI
    output_img.save(TXT_OUTPUT_PNG, dpi=template_dpi)

    # Create PDF
    pdf = FPDF(orientation='P', unit='pt', format=[text_width_margin_pt, text_height_margin_pt])
    pdf.add_page()
    pdf.image(TXT_OUTPUT_PNG, x=text_margin_pt, y=text_margin_pt, w=text_width_pt, h=text_height_pt)

    pdf.output(os.path.abspath(TXT_OUTPUT_PDF))

    send_to_printer(os.path.abspath(TXT_OUTPUT_PDF), printer_ip, printer_port)

def generate_qr_design(qr_text, number, printer_ip, printer_port):

    # Open the template image
    template_img = Image.open(os.path.abspath(QR_TEMPLATE)).convert("RGBA")
    template_w, template_h = template_img.size
    template_dpi = template_img.info.get('dpi', (CONFIG_DPI, CONFIG_DPI))

    # Calculate the scale for the QR code
    scale = template_w // QR_SCALE_FACTOR

    # Generate the QR code using segno
    qr_code = segno.make_qr(qr_text)
    qr_code.save(QR_OUTPUT_PNG, scale=scale, border=0, dark='black', light=None)

    # Open the saved QR code image
    qr_img = Image.open(QR_OUTPUT_PNG).convert("RGBA")
    qr_w, qr_h = qr_img.size

    # Create a copy of the template image to modify
    output_img = template_img.copy()

    # Calculate the position to paste the QR code
    qr_x = (template_w - qr_w) // 2 - QR_X_OFFSET
    qr_y = (template_h - qr_h) // 2 + QR_Y_OFFSET

    # Paste the QR code onto the template
    output_img.paste(qr_img, (qr_x, int(qr_y)), qr_img)

    # Prepare to draw the numeric code
    draw = ImageDraw.Draw(output_img)
    font = ImageFont.truetype(CONFIG_FONT, QR_TEXT_FONT_SIZE)

    # Calculate the position for the numeric code text
    text_x = template_w // 2 - QR_TEXT_X_OFFSET
    text_y = template_h - QR_TEXT_Y_OFFSET

    # Draw the numeric code text onto the image
    draw.text((text_x, text_y), number, font=font, fill="black", anchor="mm")

    # Save the final image with the correct DPI
    output_img.save(QR_OUTPUT_PNG, dpi=template_dpi)

    # Create PDF
    pdf = FPDF(orientation='P', unit='pt', format=[qr_width_margin_pt, qr_height_margin_pt])
    pdf.add_page()
    pdf.image(QR_OUTPUT_PNG, x=qr_margin_pt, y=qr_margin_pt, w=qr_width_pt, h=qr_height_pt)

    # Save the PDF as a file
    pdf.output(os.path.abspath(QR_OUTPUT_PDF))

    send_to_printer(os.path.abspath(QR_OUTPUT_PDF), printer_ip, printer_port)

def generate_polyaire_design(qr_text, number, printer_ip, printer_port):

    # Open the template image
    template_img = Image.open(os.path.abspath(POLYAIRE_TEMPLATE)).convert("RGBA")
    template_w, template_h = template_img.size
    template_dpi = template_img.info.get('dpi', (CONFIG_DPI, CONFIG_DPI))

    # Generate the QR code using segno
    qr_code = segno.make_qr(qr_text)
    qr_code.save(POLYAIRE_OUTPUT_PNG, scale=5, border=0, dark='black', light=None)

    # Open the saved QR code image
    qr_img = Image.open(POLYAIRE_OUTPUT_PNG).convert("RGBA")
    qr_w, qr_h = qr_img.size

    # Resize the QR code image to the desired scale factor (4.25)
    qr_img = qr_img.resize((int(qr_w * POLYAIRE_SCALE_FACTOR / 5), int(qr_h * POLYAIRE_SCALE_FACTOR / 5)), Image.LANCZOS)
    qr_w, qr_h = qr_img.size

    # Create a copy of the template image to modify
    output_img = template_img.copy()

    # Calculate the position to paste the QR code
    qr_x = (template_w - qr_w) // 2 - POLYAIRE_X_OFFSET
    qr_y = (template_h - qr_h) // 2 + POLYAIRE_Y_OFFSET

    # Paste the QR code onto the template
    output_img.paste(qr_img, (qr_x, int(qr_y)), qr_img)

    # Prepare to draw the numeric code
    draw = ImageDraw.Draw(output_img)
    font = ImageFont.truetype(CONFIG_FONT, POLYAIRE_TEXT_FONT_SIZE)

    # Calculate the position for the numeric code text
    text_x = template_w // 2 - POLYAIRE_TEXT_X_OFFSET
    text_y = template_h - POLYAIRE_TEXT_Y_OFFSET

    # Draw the numeric code text onto the image
    draw.text((text_x, text_y), number, font=font, fill="black", anchor="mm")

    # Save the final image with the correct DPI
    output_img.save(POLYAIRE_OUTPUT_PNG, dpi=template_dpi)

    # Create PDF
    pdf = FPDF(orientation='P', unit='pt', format=[polyaire_width_margin_pt, polyaire_height_margin_pt])
    pdf.add_page()
    pdf.image(POLYAIRE_OUTPUT_PNG, x=polyaire_margin_pt, y=polyaire_margin_pt, w=polyaire_width_pt, h=polyaire_height_pt)

    # Save the PDF as a file
    pdf.output(os.path.abspath(POLYAIRE_OUTPUT_PDF))

    send_to_printer(os.path.abspath(POLYAIRE_OUTPUT_PDF), printer_ip, printer_port)

# Sample usage
# generate_qr_design(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
generate_label_design(sys.argv[2], sys.argv[3], sys.argv[4])
generate_polyaire_design(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])