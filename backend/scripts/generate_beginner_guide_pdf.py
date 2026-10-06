import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "SATHI — AI & Machine Learning Architecture Guide (Beginner Edition)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 756, 576, 756)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 22, page_str)
        self.drawString(36, 22, "Confidential & Educational — SIH26001 / SATHI Disaster Management System")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 30, 576, 30)
        self.restoreState()


def build_pdf(filename="SATHI_AI_System_Beginners_Guide.pdf"):
    # Printable area: 612 - 72 = 540 width; 792 - 64 = 728 height
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=12,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11.2,
        textColor=colors.HexColor('#334155'),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor('#334155'),
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=11.0,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.0,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.8,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.4,
        leading=9.8,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # ================= COVER BANNER =================
    story.append(Paragraph("SATHI AI & Machine Learning Architecture", title_style))
    story.append(Paragraph("A Complete, Beginner-Friendly Guide to Landslide Early Warning & Flood Management AI", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#2563EB'), spaceBefore=0, spaceAfter=6))

    # Executive Overview Callout
    callout_data = [[
        Paragraph(
            "<b>What is SATHI?</b> "
            "<b>SATHI</b> (Smart Automated Terrain Hazard Intelligence) is an intelligent early-warning platform designed for "
            "vulnerable regions across North-East India. It combines <b>satellite observation data</b>, <b>IoT ground telemetry</b>, "
            "and <b>7 specialized Machine Learning algorithms</b> to predict landslides before they happen and optimize emergency rescue operations when floods occur.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[540])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 4))

    # ================= CHAPTER 1 =================
    story.append(Paragraph("1. How SATHI Works (The 30,000-Foot View)", h1_style))
    story.append(Paragraph(
        "Imagine you are a disaster manager looking at an entire state like Assam, Meghalaya, or Mizoram. "
        "A landslide or flash flood happens because of three compounding factors: <b>weak soil/steep rock</b>, <b>heavy continuous monsoon rain</b>, and <b>topographic elevation</b>. "
        "Humans cannot manually monitor thousands of mountain kilometers every second. That is why SATHI uses an <b>Automated AI Brain</b> operating in three continuous steps:",
        body_style
    ))
    story.append(Paragraph("• <b>Step 1 — Sense:</b> Satellite radars (AlphaEarth / Sentinel) look at ground movement from space, while ground IoT sensors measure rainfall and soil moisture.", bullet_style))
    story.append(Paragraph("• <b>Step 2 — Think:</b> The AI model takes 109 physical and environmental numbers and calculates the exact probability (0% to 100%) of a landslide occurring within the next 24 hours.", bullet_style))
    story.append(Paragraph("• <b>Step 3 — Act:</b> The system broadcasts live alerts over WebSockets directly to the live map, sounding sirens and generating rescue priorities.", bullet_style))
    
    story.append(Spacer(1, 4))

    # ================= CHAPTER 2 =================
    story.append(Paragraph("2. The Primary Landslide Early-Warning Brain (XGBoost Classifier)", h1_style))
    story.append(Paragraph(
        "The core model for landslide prediction is called <b>XGBoost (Extreme Gradient Boosting)</b>. "
        "Think of XGBoost like a committee of 100 expert scientists. The first scientist makes a prediction; the second scientist looks at where the first was mistaken and corrects it; "
        "and so on, until all 100 scientists combine their wisdom to produce a fast, highly accurate answer in under <b>15 milliseconds</b>.",
        body_style
    ))

    story.append(Paragraph("The 5 Core Feature Categories Given to the AI:", h2_style))

    # Table of Features
    feature_headers = [
        Paragraph("<b>Feature Category</b>", table_header_style),
        Paragraph("<b>What it Measures</b>", table_header_style),
        Paragraph("<b>Why it Matters for Landslides</b>", table_header_style)
    ]
    feature_rows = [
        feature_headers,
        [
            Paragraph("<b>1. Antecedent Rainfall</b>", table_cell_bold),
            Paragraph("1h, 24h, 3-day, 7-day, and 14-day cumulative rainfall (mm)", table_cell_style),
            Paragraph("<b>62.7% Model Importance!</b> Mountains don't collapse from 1 minute of rain; they collapse when weeks of rain saturate the soil sponge.", table_cell_style)
        ],
        [
            Paragraph("<b>2. Topographic Terrain</b>", table_cell_bold),
            Paragraph("Slope angle (°), elevation (m), aspect, and Topographic Wetness Index (TWI)", table_cell_style),
            Paragraph("<b>33.4% Model Importance!</b> Steep slopes (>25°) under gravity slide much more easily than flat valleys.", table_cell_style)
        ],
        [
            Paragraph("<b>3. Soil Moisture & Pore Pressure</b>", table_cell_bold),
            Paragraph("Volumetric soil moisture at 0-7cm and 7-28cm depth layers", table_cell_style),
            Paragraph("As water fills pore spaces between dirt particles, it creates hydraulic pressure that liquefies mud.", table_cell_style)
        ],
        [
            Paragraph("<b>4. AlphaEarth Embeddings</b>", table_cell_bold),
            Paragraph("64-dimensional feature vector from Google Earth Engine satellite scans", table_cell_style),
            Paragraph("Captures surface vegetation health, deforestation, rock fractures, and radar displacement from space.", table_cell_style)
        ],
        [
            Paragraph("<b>5. Infrastructure & History</b>", table_cell_bold),
            Paragraph("Distance to roads, rivers, faults, and historical landslide incident count", table_cell_style),
            Paragraph("Road excavations cut into toe-slopes of hills, making human-disturbed slopes historically more vulnerable.", table_cell_style)
        ]
    ]

    feat_table = Table(feature_rows, colWidths=[125, 175, 240])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(feat_table)
    story.append(Spacer(1, 4))

    # Risk Categories Callout Box
    story.append(Paragraph("How the AI Categorizes Threat (4 Risk Tiers):", h2_style))
    tier_data = [
        [
            Paragraph("<font color='#16A34A'><b>LOW RISK (0 - 24)</b></font><br/>Normal conditions. Soil is dry; rainfall is manageable. Standard automated monitoring.", table_cell_style),
            Paragraph("<font color='#2563EB'><b>FLOOD WATCH (25 - 49)</b></font><br/>Rising river gauge levels or moderate slope saturation. Lowland flood advisories activated.", table_cell_style),
        ],
        [
            Paragraph("<font color='#EA580C'><b>HIGH RISK (50 - 74)</b></font><br/>Active slope creep detected. Heavy rainfall threshold breached. Heavy earthmovers on standby.", table_cell_style),
            Paragraph("<font color='#DC2626'><b>CRITICAL DANGER (75 - 100)</b></font><br/>Imminent failure within 24h. Immediate emergency evacuation orders broadcast to civil authorities.", table_cell_style)
        ]
    ]
    tier_table = Table(tier_data, colWidths=[270, 270])
    tier_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 6))

    # ================= CHAPTER 3 =================
    story.append(Paragraph("3. The 7 Multi-Hazard Flood & Disaster ML Modules", h1_style))
    story.append(Paragraph(
        "Beyond predicting landslides, SATHI includes a complete <b>Flood Disaster Management AI Suite</b>. "
        "When disaster strikes, authorities cannot just rely on intuition; they need mathematical optimization for triage, rescue boats, and supply distribution.",
        body_style
    ))

    disaster_headers = [
        Paragraph("<b>#</b>", table_header_style),
        Paragraph("<b>Disaster Module</b>", table_header_style),
        Paragraph("<b>AI Algorithm</b>", table_header_style),
        Paragraph("<b>What it Solves in Real Emergencies</b>", table_header_style)
    ]
    disaster_rows = [
        disaster_headers,
        [
            Paragraph("<b>1</b>", table_cell_bold),
            Paragraph("<b>Flood Severity Assessment</b>", table_cell_bold),
            Paragraph("Physics & Topographic Embedding", table_cell_style),
            Paragraph("Calculates water depth (e.g. 2.8 meters) and inundation boundaries from rainfall and river proximity.", table_cell_style)
        ],
        [
            Paragraph("<b>2</b>", table_cell_bold),
            Paragraph("<b>Rescue Priority Identification</b>", table_cell_bold),
            Paragraph("Random Forest Triage Classifier", table_cell_style),
            Paragraph("Ranks neighborhoods (P1 Critical, P2 Urgent, P3 Routine) by weighing population, SOS volume, and water depth.", table_cell_style)
        ],
        [
            Paragraph("<b>3</b>", table_cell_bold),
            Paragraph("<b>Resource Allocation Optimizer</b>", table_cell_bold),
            Paragraph("XGBoost Regression Optimizer", table_cell_style),
            Paragraph("Computes exact disaster relief needs: clean drinking water (litres), food rations, trauma kits, and rescue boats.", table_cell_style)
        ],
        [
            Paragraph("<b>4</b>", table_cell_bold),
            Paragraph("<b>Area Severity Clustering</b>", table_cell_bold),
            Paragraph("K-Means Clustering", table_cell_style),
            Paragraph("Groups hundreds of flooded GPS points into 3-5 operational rescue clusters for NDRF command centers.", table_cell_style)
        ],
        [
            Paragraph("<b>5</b>", table_cell_bold),
            Paragraph("<b>SOS Request Classifier</b>", table_cell_bold),
            Paragraph("NLP Transformer (DistilBERT)", table_cell_style),
            Paragraph("Reads frantic citizen SMS/social posts, extracts urgency, and categorizes into Medical, Evacuation, or Food needs.", table_cell_style)
        ],
        [
            Paragraph("<b>6</b>", table_cell_bold),
            Paragraph("<b>Damage Assessment</b>", table_cell_bold),
            Paragraph("Structural Hydrodynamic Model", table_cell_style),
            Paragraph("Estimates collapse hazard for bridges, concrete buildings, and roads based on water flow velocity.", table_cell_style)
        ],
        [
            Paragraph("<b>7</b>", table_cell_bold),
            Paragraph("<b>Safe Route Recommendation</b>", table_cell_bold),
            Paragraph("Dijkstra / A* Graph Engine", table_cell_style),
            Paragraph("Computes rescue paths between origin and shelters while dynamically steering away from submerged danger zones.", table_cell_style)
        ]
    ]

    disaster_table = Table(disaster_rows, colWidths=[18, 132, 120, 270])
    disaster_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(disaster_table)
    story.append(Spacer(1, 6))

    # ================= CHAPTER 4 =================
    story.append(Paragraph("4. The End-to-End Real-Time Pipeline", h1_style))
    story.append(Paragraph(
        "Here is the exact journey of a single sensor reading through the software stack:",
        body_style
    ))

    pipeline_steps = [
        [
            Paragraph("<b>1. Ingestion</b>", table_cell_bold),
            Paragraph("An IoT hill station transmits telemetry: <i>Temperature: 26°C, Humidity: 85%, Soil: 48%, Rain: 45mm</i>.", table_cell_style)
        ],
        [
            Paragraph("<b>2. Feature Assembly</b>", table_cell_bold),
            Paragraph("The FastAPI backend combines this live reading with historical rainfall windows (3d, 7d, 14d) and GIS slope maps.", table_cell_style)
        ],
        [
            Paragraph("<b>3. Model Inference</b>", table_cell_bold),
            Paragraph("The XGBoost model evaluates the 109-element feature vector and outputs a <b>Risk Score: 88 (CRITICAL)</b> in <15ms.", table_cell_style)
        ],
        [
            Paragraph("<b>4. Database Save</b>", table_cell_bold),
            Paragraph("The prediction record and timestamp are persisted in MySQL (or SQLite offline store) for historical trend auditing.", table_cell_style)
        ],
        [
            Paragraph("<b>5. WebSocket Broadcast</b>", table_cell_bold),
            Paragraph("The native WebSocket server (`/ws/risk`) pushes the live JSON event to all connected React dashboards and live maps.", table_cell_style)
        ],
        [
            Paragraph("<b>6. Map UI Update</b>", table_cell_bold),
            Paragraph("The user's web browser pulses the affected mountain polygon red, sounds alerts, and lists actionable evacuation steps.", table_cell_style)
        ]
    ]
    pipe_table = Table(pipeline_steps, colWidths=[120, 420])
    pipe_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(pipe_table)
    story.append(Spacer(1, 6))

    # ================= CHAPTER 5 =================
    story.append(Paragraph("5. Summary Glossary for Beginners", h1_style))
    glossary = [
        "• <b>Machine Learning (ML):</b> Teaching a computer to recognize patterns from thousands of past landslide events instead of hardcoding static if-else rules.",
        "• <b>Inference:</b> The moment the trained AI looks at new live sensor data and calculates a risk prediction.",
        "• <b>Embeddings (AlphaEarth):</b> Translating high-resolution satellite imagery into a compact list of 64 meaningful numbers representing ground health.",
        "• <b>Antecedent Rainfall:</b> Rain that fell days or weeks ago that remains trapped underground, saturating rock layers.",
        "• <b>WebSocket:</b> A two-way open internet pipe allowing the server to push live data to your screen instantly without having to refresh the page."
    ]
    for g in glossary:
        story.append(Paragraph(g, bullet_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "SATHI_AI_System_Beginners_Guide.pdf")
    build_pdf(out_path)
