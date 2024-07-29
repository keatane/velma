from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(input, output="results.pdf", title="Analysis Report - VELMA"):

    with open(input, 'r') as file:
        text = file.read()

    c = canvas.Canvas(output, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)
    c.setFont("Helvetica", 12)

    y_position = 700
    counter = 0
    for line in text.split('\n'):
        counter += 1
        c.drawString(100, y_position, line)
        y_position -= 20
        if counter % 30 == 0:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 700
            counter = 0
    c.save()