from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, Image as RLImage,
                                 HRFlowable, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import os

ORANGE = colors.HexColor('#D4A017')
GRIS   = colors.HexColor('#555555')
NOIR   = colors.HexColor('#222222')

W, H = A4


def _img(filename):
    base = os.path.dirname(__file__)
    candidates = [
        os.path.join(base, '..', 'static', filename),
        os.path.join(base, '..', 'staticfiles', filename),
        os.path.join(base, filename),
        os.path.join('/app', 'static', filename),
        os.path.join('/app', 'staticfiles', filename),
        os.path.join('/app', filename),
    ]
    for p in candidates:
        p = os.path.normpath(p)
        if os.path.exists(p):
            return p
    return None


TEXTES = {
    'fr': {
        'objet_label': 'Objet :',
        'objet_texte': 'Offre de services, présentation de notre société ESVE – Ecology Smart Vision Equipement',
        'salutation':  'Madame, Monsieur,',
        'intro': ("Nous avons le plaisir de vous adresser la présente lettre afin de vous présenter notre entreprise, "
                  "<b>ESVE – Ecology Smart Vision Equipement</b>, spécialisée dans la fourniture de solutions techniques "
                  "à fortes valeurs ajoutées et à destination des secteurs des mines, des carrières, du BTP et des industries."),
        'p1': ("Implantée au Burkina Faso, ESVE s'est donnée pour mission d'accompagner les opérateurs industriels dans "
               "l'optimisation de leur productivité, la réduction de leurs coûts opérationnels, ainsi que le respect des "
               "normes environnementales et de sécurité. Notre approche repose sur des valeurs fondamentales : "
               "<b>la qualité, la réactivité et l'adaptabilité aux réalités du terrain.</b>"),
        'p2': ("Afin de garantir la fiabilité et la performance de nos prestations, ESVE collabore avec un panel des "
               "meilleurs fournisseurs locaux et internationaux, rigoureusement sélectionnés pour leur expertise, "
               "leur innovation et leur conformité aux standards internationaux."),
        'p3': ("Parfaitement consciente des enjeux techniques, logistiques et environnementaux propres au secteur minier "
               "burkinabè, ESVE se positionne aujourd'hui comme un partenaire stratégique de confiance, capable de proposer "
               "des solutions robustes, durables et opérationnelles dès leur mise en œuvre. Grâce à une expertise locale, "
               "nous offrons à nos clients un accompagnement sur mesure, répondant à leurs impératifs d'efficacité, "
               "de rentabilité et de responsabilité sociétale."),
        'p4': ("Dans le cadre du développement de nos activités et dans l'optique de collaborer avec votre structure, "
               "nous sollicitons notre référencement au sein de votre base de données fournisseurs, afin de pouvoir être "
               "consultés pour toute demande ou besoin en lien avec nos domaines de compétences et d'intervention."),
        'attente': "Dans l'attente de votre retour, veuillez recevoir, Madame, Monsieur, l'expression de nos salutations distinguées.",
        'domaines': "Nos principaux domaines de compétences et d'intervention :",
        'd1_titre': "Fourniture d'outils d'attaque au sol (O.A.S / G.E.T.) et trains de roulement (T.D.R / U.C)",
        'd1_texte': ("ESVE propose une large gamme de dents, porte-dents, boucliers, lames et adaptateurs compatibles avec les "
                     "équipements des plus grands fabricants tels que Caterpillar, Komatsu, Hensley et ESCO, destinés aux engins "
                     "de mines, de carrières et de travaux publics ainsi que les trains de roulement des équipements mobiles."),
        'd2_titre': "Fourniture de pièces et composants mécaniques",
        'd2_texte': ("Nous disposons d'un portefeuille de pièces de rechange et composants mécaniques (moteurs, boîtes de "
                     "transmissions, convertisseurs de couple, pompes hydrauliques, vérins, systèmes hydrauliques…), neuf, "
                     "reconditionné en atelier ou chez le constructeur pour les équipements Caterpillar, Komatsu et Volvo."),
        'd3_titre': "Location d'équipements industriels et BTP",
        'd3_texte': ("Afin de répondre aux besoins temporaires ou urgents de vos chantiers, nous mettons à disposition un parc "
                     "de matériels en location : pelles, chargeuses, groupes électrogènes, compresseurs, etc."),
        'd4_titre': "Service technique et accompagnement",
        'd4_texte': ("Nos équipes qualifiées assurent l'installation, la maintenance et le suivi technique des équipements "
                     "fournis, avec un service après-vente réactif et proche de vos sites d'opération."),
        'footer_left':  "ECOLOGY SMART VISION EQUIPEMENT\nS/C 04 BP 398 OUAGA 04 — Secteur 42 OUAGADOUGOU\n(+226) 05 56 25 92 — direction@svequipement.com",
        'footer_right': "N° RIB : BF148-01001-077355324101-26\nN° RCCM : BF-OUA-01-2025-B13-08308\nN° IFU : 00272062K — Régime : RSI",
    },
    'en': {
        'objet_label': 'Subject:',
        'objet_texte': 'Service Offer — Presentation of ESVE – Ecology Smart Vision Equipement',
        'salutation':  'Dear Sir/Madam,',
        'intro': ("We are pleased to present our company, <b>ESVE – Ecology Smart Vision Equipement</b>, specialised in "
                  "the supply of high-value technical solutions for the mining, quarrying, construction and industrial sectors."),
        'p1': ("Based in Burkina Faso, ESVE's mission is to help industrial operators optimise their productivity, reduce "
               "operational costs, and comply with environmental and safety standards. Our approach is built on core values: "
               "<b>quality, responsiveness and adaptability to field realities.</b>"),
        'p2': ("To guarantee the reliability and performance of our services, ESVE works with a panel of the best local and "
               "international suppliers, rigorously selected for their expertise, innovation and compliance with international standards."),
        'p3': ("Fully aware of the technical, logistical and environmental challenges of the Burkinabe mining sector, ESVE "
               "positions itself as a trusted strategic partner delivering robust, sustainable solutions. Thanks to local expertise, "
               "we offer tailor-made support meeting requirements for efficiency, profitability and social responsibility."),
        'p4': ("As part of the development of our activities, we request to be registered in your supplier database so that "
               "we may be consulted for any request or need related to our areas of expertise."),
        'attente': "We look forward to hearing from you and remain at your disposal for any further information.",
        'domaines': "Our main areas of expertise:",
        'd1_titre': "Supply of Ground Engaging Tools (G.E.T. / O.A.S) and Undercarriage Components (U.C / T.D.R)",
        'd1_texte': ("ESVE offers a wide range of teeth, adapters, shrouds, blades and cutting edges compatible with Caterpillar, "
                     "Komatsu, Hensley and ESCO equipment for mining, quarrying and civil engineering, "
                     "as well as undercarriage components for mobile equipment."),
        'd2_titre': "Supply of Mechanical Parts and Components",
        'd2_texte': ("We hold a portfolio of spare parts and mechanical components (engines, gearboxes, torque converters, "
                     "hydraulic pumps, cylinders, hydraulic systems…), new or reconditioned, "
                     "for Caterpillar, Komatsu and Volvo equipment."),
        'd3_titre': "Industrial and Construction Equipment Rental",
        'd3_texte': ("To meet the temporary or urgent needs of your sites, we provide a fleet of equipment for rental: "
                     "excavators, loaders, generators, compressors, etc."),
        'd4_titre': "Technical Service and Support",
        'd4_texte': ("Our qualified teams provide installation, maintenance and technical monitoring of the equipment supplied, "
                     "with a reactive after-sales service close to your operating sites."),
        'footer_left':  "ECOLOGY SMART VISION EQUIPEMENT\nS/C 04 BP 398 OUAGA 04 — Secteur 42 OUAGADOUGOU\n(+226) 05 56 25 92 — direction@svequipement.com",
        'footer_right': "RIB: BF148-01001-077355324101-26\nRCCM: BF-OUA-01-2025-B13-08308\nIFU: 00272062K — Tax regime: RSI",
    }
}

MARGIN_L = 1.8*cm
MARGIN_R = 1.8*cm
MARGIN_T = 1.5*cm
MARGIN_B = 2.8*cm
CONTENT_W = W - MARGIN_L - MARGIN_R  # ~17.4cm


def _draw_header(canvas, logo_p):
    """Dessine l'en-tête sur chaque page (logo gauche + slogan centre)."""
    canvas.saveState()
    y_top = H - MARGIN_T

    if logo_p and os.path.exists(logo_p):
        logo_h = 3.2*cm
        logo_w = 3.2*cm
        canvas.drawImage(logo_p, MARGIN_L, y_top - logo_h,
                         width=logo_w, height=logo_h,
                         preserveAspectRatio=True, mask='auto')

    # Slogan centré
    canvas.setFont('Helvetica-Bold', 20)
    canvas.setFillColor(ORANGE)
    canvas.drawCentredString(W / 2, y_top - 2.0*cm, 'The Supplier You Need')

    # Ligne sous l'en-tête
    canvas.setStrokeColor(ORANGE)
    canvas.setLineWidth(1.5)
    line_y = y_top - 3.4*cm
    canvas.line(MARGIN_L, line_y, W - MARGIN_R, line_y)

    canvas.restoreState()
    return line_y  # position y après la ligne


def _draw_footer(canvas, T, is_last):
    """Dessine le footer 2 colonnes uniquement sur la dernière page."""
    if not is_last:
        return
    canvas.saveState()
    y = 1.8*cm
    canvas.setStrokeColor(GRIS)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_L, y + 0.5*cm, W - MARGIN_R, y + 0.5*cm)

    # Colonne gauche
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRIS)
    for i, line in enumerate(T['footer_left'].split('\n')):
        canvas.drawString(MARGIN_L, y - i * 0.32*cm, line)

    # Colonne droite
    for i, line in enumerate(T['footer_right'].split('\n')):
        canvas.drawRightString(W - MARGIN_R, y - i * 0.32*cm, line)

    canvas.restoreState()


def generer_pdf_offre(data: dict) -> bytes:
    langue  = data.get('langue', 'fr')
    T       = TEXTES[langue]
    buf     = BytesIO()
    logo_p  = _img('logo-esve.jpg') or _img('logo-esve.png')
    prod_p  = _img('esve_products.png')
    field_p = _img('esve_field.png')

    # Styles
    s_n  = ParagraphStyle('n',  fontSize=10, leading=15, alignment=TA_JUSTIFY,
                           spaceAfter=7, fontName='Helvetica')
    s_b  = ParagraphStyle('b',  fontSize=10, leading=15, alignment=TA_JUSTIFY,
                           fontName='Helvetica-Bold', spaceAfter=7)
    s_r  = ParagraphStyle('r',  fontSize=9,  leading=13, alignment=TA_RIGHT,
                           textColor=GRIS, fontName='Helvetica')
    s_t  = ParagraphStyle('t',  fontSize=11, leading=14, fontName='Helvetica-Bold',
                           textColor=ORANGE, spaceAfter=5)
    s_o  = ParagraphStyle('o',  fontSize=10, leading=14, fontName='Helvetica-Bold',
                           spaceAfter=8)

    # Espace sous l'en-tête (logo 3.2cm + ligne 3.4cm + marge)
    HEADER_SPACE = 3.8*cm

    total_pages = [0]

    def on_page(canvas, doc):
        _draw_header(canvas, logo_p)
        _draw_footer(canvas, T, doc.page == total_pages[0])

    # ── STORY ────────────────────────────────────────────────────────────────
    def make_story():
        els = []
        els.append(Spacer(1, HEADER_SPACE))

        # Destinataires à droite (société, noms, adresse, date)
        soc = (data.get('societe') or '').strip()
        if soc:
            els.append(Paragraph(f'<b>{soc}</b>', s_r))
        for d in (data.get('destinataires') or [])[:3]:
            nom = (d.get('nom') or '').strip()
            fn  = (d.get('fonction') or '').strip()
            if nom or fn:
                els.append(Paragraph(
                    (f'<b>{nom}</b>' if nom else '') + (f'  –  {fn}' if fn else ''), s_r))
        adresse = (data.get('adresse') or '').strip()
        if adresse:
            els.append(Paragraph(adresse, s_r))
        date_doc = (data.get('date_doc') or '').strip()
        if date_doc:
            els.append(Paragraph(
                f'Ouagadougou, le {date_doc}' if langue == 'fr' else f'Ouagadougou, {date_doc}',
                s_r))
        els.append(Spacer(1, 0.5*cm))

        # Corps lettre page 1
        els.append(Paragraph(f'{T["objet_label"]} <b>{T["objet_texte"]}</b>', s_o))
        els.append(Paragraph(T['salutation'], s_b))
        els.append(Spacer(1, 0.15*cm))
        for k in ['intro', 'p1', 'p2', 'p3', 'p4']:
            els.append(Paragraph(T[k], s_n))
        custom = (data.get('texte_custom') or '').strip()
        if custom:
            els.append(Paragraph(custom, s_n))
        els.append(Spacer(1, 0.3*cm))
        els.append(Paragraph(T['attente'], s_n))

        # ── PAGE 2 ────────────────────────────────────────────────────────────
        els.append(PageBreak())
        els.append(Spacer(1, HEADER_SPACE))

        els.append(Paragraph(f'<b>{T["domaines"]}</b>', s_b))
        els.append(Spacer(1, 0.2*cm))

        els.append(Paragraph(T['d1_titre'], s_t))
        els.append(Paragraph(T['d1_texte'], s_n))
        els.append(Spacer(1, 0.15*cm))
        els.append(Paragraph(T['d2_titre'], s_t))
        els.append(Paragraph(T['d2_texte'], s_n))

        # Grille photos produits (C9) — en bas de page 2
        if prod_p:
            els.append(Spacer(1, 0.25*cm))
            els.append(RLImage(prod_p, width=CONTENT_W, height=12.5*cm))

        # ── PAGE 3 ────────────────────────────────────────────────────────────
        els.append(PageBreak())
        els.append(Spacer(1, HEADER_SPACE))

        els.append(Paragraph(T['d3_titre'], s_t))
        els.append(Paragraph(T['d3_texte'], s_n))
        els.append(Spacer(1, 0.15*cm))
        els.append(Paragraph(T['d4_titre'], s_t))
        els.append(Paragraph(T['d4_texte'], s_n))

        # Image terrain (C8) — un peu moins haute pour ne pas coller au footer
        if field_p:
            els.append(Spacer(1, 0.5*cm))
            els.append(RLImage(field_p, width=CONTENT_W, height=12*cm))
            els.append(Spacer(1, 0.8*cm))

        return els

    # Pré-build pour compter les pages
    tmp  = BytesIO()
    dtmp = SimpleDocTemplate(tmp, pagesize=A4,
                             rightMargin=MARGIN_R, leftMargin=MARGIN_L,
                             topMargin=MARGIN_T, bottomMargin=MARGIN_B)
    class PC:
        count = 0
        def __call__(self, c, d): self.count = d.page
    pc = PC()
    dtmp.build(make_story(), onFirstPage=pc, onLaterPages=pc)
    total_pages[0] = pc.count

    # Build final
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=MARGIN_R, leftMargin=MARGIN_L,
                            topMargin=MARGIN_T, bottomMargin=MARGIN_B)
    doc.build(make_story(), onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()