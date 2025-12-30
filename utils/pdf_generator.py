"""
PDF generation utility for VAPH Module A reports.
Converts markdown-formatted text to a well-formatted PDF document.
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
import re


def parse_markdown_to_elements(text: str, styles):
    """
    Parse markdown-formatted text and convert to ReportLab elements.
    Handles:
    - **bold** text (questions)
    - Regular text (answers)
    - Line breaks
    """
    elements = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 0.3 * cm))
            continue
        
        # Check if line contains bold markdown (**text**)
        if '**' in line:
            # Split by ** and process
            parts = re.split(r'(\*\*.*?\*\*)', line)
            para_parts = []
            
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    # Bold text (question)
                    bold_text = part[2:-2]  # Remove **
                    para_parts.append(f'<b>{bold_text}</b>')
                elif part:
                    # Regular text (answer)
                    para_parts.append(part)
            
            para_text = ''.join(para_parts)
            elements.append(Paragraph(para_text, styles['Normal']))
        else:
            # Regular paragraph
            elements.append(Paragraph(line, styles['Normal']))
        
        elements.append(Spacer(1, 0.2 * cm))
    
    return elements


def generate_pdf_from_text(text: str, title: str = "VAPH Module A Rapport", code: str = "") -> BytesIO:
    """
    Generate a PDF document from markdown-formatted text.
    
    Args:
        text: The markdown-formatted text content
        title: Title for the document
        code: Disorder code (optional, for filename/header)
    
    Returns:
        BytesIO object containing the PDF data
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=(0, 0, 0),
        spaceAfter=0.5*cm,
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=(0.2, 0.2, 0.2),
        spaceAfter=0.3*cm,
        alignment=TA_LEFT
    )
    
    # Normal style with better spacing
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=0.2*cm,
        alignment=TA_LEFT
    )
    
    styles.add(title_style)
    styles.add(subtitle_style)
    styles.add(normal_style)
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(title, styles['CustomTitle']))
    if code:
        story.append(Paragraph(f"Stoorniscode: <b>{code}</b>", styles['CustomSubtitle']))
    story.append(Spacer(1, 0.5 * cm))
    
    # Parse and add content
    content_elements = parse_markdown_to_elements(text, {
        'Normal': styles['CustomNormal'],
        'Heading1': styles['Heading1'],
        'Heading2': styles['Heading2']
    })
    story.extend(content_elements)
    
    # Build PDF
    doc.build(story)
    
    # Reset buffer position
    buffer.seek(0)
    return buffer


def generate_pdf_for_code(output_text: str, code: str) -> BytesIO:
    """
    Convenience function to generate PDF for a specific disorder code.
    
    Args:
        output_text: The generated Module A answers (markdown format)
        code: The disorder code
    
    Returns:
        BytesIO object containing the PDF data
    """
    title = f"VAPH Module A - Stoorniscode {code}"
    return generate_pdf_from_text(output_text, title=title, code=code)

