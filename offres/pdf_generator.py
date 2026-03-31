from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from django.conf import settings
from io import BytesIO
import os

ORANGE_ESVE = colors.HexColor('#D4A017')
DARK_ESVE   = colors.HexColor('#1A1A2E')
GRIS        = colors.HexColor('#555555')
BLANC       = colors.white


def get_logo_path():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo-esve.jpg')
    return logo_path if os.path.exists(logo_path) else None


# ── Textes bilingues ──────────────────────────────────────────────────────────
TEXTES = {
    'fr': {
        'objet_label':   'Objet :',
        'objet_texte':   'Offre de services, présentation de notre société ESVE – Ecology Smart Vision Equipement',
        'salutation':    'Madame, Monsieur,',
        'intro': (
            "Nous avons le plaisir de vous adresser la présente lettre afin de vous présenter notre entreprise, "
            "<b>ESVE – Ecology Smart Vision Equipement</b>, spécialisée dans la fourniture de solutions techniques "
            "à fortes valeurs ajoutées et à destination des secteurs des mines, des carrières, du BTP et des industries."
        ),
        'p1': (
            "Implantée au Burkina Faso, ESVE s'est donnée pour mission d'accompagner les opérateurs industriels dans "
            "l'optimisation de leur productivité, la réduction de leurs coûts opérationnels, ainsi que le respect des "
            "normes environnementales et de sécurité. Notre approche repose sur des valeurs fondamentales : "
            "<b>la qualité, la réactivité et l'adaptabilité aux réalités du terrain.</b>"
        ),
        'p2': (
            "Afin de garantir la fiabilité et la performance de nos prestations, ESVE collabore avec un panel des "
            "meilleurs fournisseurs locaux et internationaux, rigoureusement sélectionnés pour leur expertise, "
            "leur innovation et leur conformité aux standards internationaux."
        ),
        'p3': (
            "Parfaitement consciente des enjeux techniques, logistiques et environnementaux propres au secteur minier "
            "burkinabè, ESVE se positionne aujourd'hui comme un partenaire stratégique de confiance, capable de proposer "
            "des solutions robustes, durables et opérationnelles dès leur mise en œuvre. Grâce à une expertise locale, "
            "nous offrons à nos clients un accompagnement sur mesure, répondant à leurs impératifs d'efficacité, "
            "de rentabilité et de responsabilité sociétale."
        ),
        'p4': (
            "Dans le cadre du développement de nos activités et dans l'optique de collaborer avec votre structure, "
            "nous sollicitons notre référencement au sein de votre base de données fournisseurs, afin de pouvoir être "
            "consultés pour toute demande ou besoin en lien avec nos domaines de compétences et d'intervention."
        ),
        'attente':  "Dans l'attente de votre retour, veuillez recevoir, Madame, Monsieur, l'expression de nos salutations distinguées.",
        'domaines': "Nos principaux domaines de compétences et d'intervention :",
        'd1_titre':  "Fourniture d'outils d'attaque au sol (O.A.S / G.E.T.) et trains de roulement (T.D.R / U.C)",
        'd1_texte': (
            "ESVE propose une large gamme de dents, porte-dents, boucliers, lames et adaptateurs compatibles avec les "
            "équipements des plus grands fabricants tels que Caterpillar, Komatsu, Hensley et ESCO, destinés aux engins "
            "de mines, de carrières et de travaux publics ainsi que les trains de roulement des équipements mobiles."
        ),
        'd2_titre': "Fourniture de pièces et composants mécaniques",
        'd2_texte': (
            "Nous disposons d'un portefeuille de pièces de rechange et composants mécaniques (moteurs, boîtes de "
            "transmissions, convertisseurs de couple, pompes hydrauliques, vérins, systèmes hydrauliques…), neuf, "
            "reconditionné en atelier ou chez le constructeur pour les équipements Caterpillar, Komatsu et Volvo."
        ),
        'd3_titre': "Location d'équipements industriels et BTP",
        'd3_texte': (
            "Afin de répondre aux besoins temporaires ou urgents de vos chantiers, nous mettons à disposition un parc "
            "de matériels en location : pelles, chargeuses, groupes électrogènes, compresseurs, etc."
        ),
        'd4_titre': "Service technique et accompagnement",
        'd4_texte': (
            "Nos équipes qualifiées assurent l'installation, la maintenance et le suivi technique des équipements "
            "fournis, avec un service après-vente réactif et proche de vos sites d'opération."
        ),
    },
    'en': {
        'objet_label':  'Subject:',
        'objet_texte':  'Service Offer — Presentation of ESVE – Ecology Smart Vision Equipement',
        'salutation':   'Dear Sir/Madam,',
        'intro': (
            "We are pleased to present our company, <b>ESVE – Ecology Smart Vision Equipement</b>, specialised in "
            "the supply of high-value technical solutions for the mining, quarrying, construction and industrial sectors."
        ),
        'p1': (
            "Based in Burkina Faso, ESVE's mission is to help industrial operators optimise their productivity, reduce "
            "operational costs, and comply with environmental and safety standards. Our approach is built on core values: "
            "<b>quality, responsiveness and adaptability to field realities.</b>"
        ),
        'p2': (
            "To guarantee the reliability and performance of our services, ESVE works with a panel of the best local and "
            "international suppliers, rigorously selected for their expertise, innovation and compliance with "
            "international standards."
        ),
        'p3': (
            "Fully aware of the technical, logistical and environmental challenges of the Burkinabe mining sector, ESVE "
            "positions itself today as a trusted strategic partner, capable of delivering robust, sustainable and "
            "immediately operational solutions. Thanks to local expertise, we offer our clients tailor-made support "
            "that meets their requirements for efficiency, profitability and social responsibility."
        ),
        'p4': (
            "As part of the development of our activities and with a view to collaborating with your organisation, we "
            "request to be registered in your supplier database so that we may be consulted for any request or need "
            "related to our areas of expertise."
        ),
        'attente':  "We look forward to hearing from you and remain at your disposal for any further information.",
        'domaines': "Our main areas of expertise:",
        'd1_titre': "Supply of Ground Engaging Tools (G.E.T. / O.A.S) and Undercarriage Components (U.C / T.D.R)",
        'd1_texte': (
            "ESVE offers a wide range of teeth, adapters, shrouds, blades and cutting edges compatible with the major "
            "manufacturers including Caterpillar, Komatsu, Hensley and ESCO, for mining, quarrying and civil engineering "
            "equipment, as well as undercarriage components for mobile equipment."
        ),
        'd2_titre': "Supply of Mechanical Parts and Components",
        'd2_texte': (
            "We hold a portfolio of spare parts and mechanical components (engines, gearboxes, torque converters, "
            "hydraulic pumps, cylinders, hydraulic systems…), new, reconditioned in workshop or by the manufacturer, "
            "for Caterpillar, Komatsu and Volvo equipment."
        ),
        'd3_titre': "Industrial and Construction Equipment Rental",
        'd3_texte': (
            "To meet the temporary or urgent needs of your sites, we provide a fleet of equipment for rental: "
            "excavators, loaders, generators, compressors, etc."
        ),
        'd4_titre': "Technical Service and Support",
        'd4_texte': (
            "Our qualified teams provide installation, maintenance and technical monitoring of the equipment supplied, "
            "with a reactive after-sales service close to your operating sites."
        ),
    }
}

FOOTER_TEXT = {
    'fr': (
        "ECOLOGY SMART VISION EQUIPEMENT  |  S/C 04 BP 398 OUAGA 04 – Secteur 42 OUAGADOUGOU  |  "
        "(+226) 05 56 25 92  |  direction@svequipement.com\n"
        "N° RIB : BF148-01001-077355324101-26  |  N° RCCM : BF-OUA-01-2025-B13-08308  |  "
        "N° IFU : 00272062K  |  Régime : RSI  |  Division fiscale : OUAGA VII"
    ),
    'en': (
        "ECOLOGY SMART VISION EQUIPEMENT  |  S/C 04 BP 398 OUAGA 04 – Secteur 42 OUAGADOUGOU  |  "
        "(+226) 05 56 25 92  |  direction@svequipement.com\n"
        "RIB: BF148-01001-077355324101-26  |  RCCM: BF-OUA-01-2025-B13-08308  |  "
        "IFU: 00272062K  |  Tax regime: RSI  |  Tax division: OUAGA VII"
    ),
}


def generer_pdf_offre(data: dict) -> bytes:
    """
    data = {
        'langue':       'fr' | 'en',
        'societe':      str,
        'destinataires': [ {'nom': str, 'fonction': str}, ... ],  # max 3
        'texte_custom': str | None,   # paragraphe libre additionnel (optionnel)
    }
    """
    langue = data.get('langue', 'fr')
    T      = TEXTES[langue]
    buffer = BytesIO()

    # ── Styles ───────────────────────────────────────────────────────────────
    s_normal  = ParagraphStyle('n',  fontSize=10, leading=15, alignment=TA_JUSTIFY,
                                spaceAfter=8)
    s_bold    = ParagraphStyle('b',  fontSize=10, leading=15, alignment=TA_JUSTIFY,
                                fontName='Helvetica-Bold', spaceAfter=8)
    s_right   = ParagraphStyle('r',  fontSize=8,  leading=12, alignment=TA_RIGHT,
                                textColor=GRIS)
    s_center  = ParagraphStyle('c',  fontSize=9,  leading=13, alignment=TA_CENTER)
    s_titre   = ParagraphStyle('t',  fontSize=11, leading=14, fontName='Helvetica-Bold',
                                textColor=ORANGE_ESVE, spaceAfter=6)
    s_objet   = ParagraphStyle('o',  fontSize=10, leading=14, fontName='Helvetica-Bold',
                                spaceAfter=10)
    s_footer  = ParagraphStyle('f',  fontSize=7.5, leading=11, alignment=TA_CENTER,
                                textColor=GRIS)

    # ── Compteur de pages pour footer uniquement sur la dernière ─────────────
    page_counter = {'total': 0, 'current': 0}

    def build_footer_table():
        ft = Table([[
            Paragraph(FOOTER_TEXT[langue].replace('\n', '<br/>'), s_footer)
        ]], colWidths=[18*cm])
        ft.setStyle(TableStyle([
            ('LINEABOVE',     (0,0), (-1,-1), 1.5, ORANGE_ESVE),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        return ft

    def on_page(canvas, doc):
        page_counter['current'] = doc.page
        canvas.saveState()
        # Footer uniquement sur la dernière page
        if doc.page == page_counter['total']:
            footer = build_footer_table()
            w, h = A4
            footer.wrapOn(canvas, w - 3*cm, 2.5*cm)
            footer.drawOn(canvas, 1.5*cm, 0.8*cm)
        canvas.restoreState()

    # ── Pré-build pour compter les pages ─────────────────────────────────────
    def build_story():
        logo_path = get_logo_path()
        elements  = []

        # En-tête
        if logo_path:
            logo = RLImage(logo_path, width=3.5*cm, height=3.5*cm)
            header_data = [[logo, Paragraph(
                '<font size="20" color="#D4A017"><b>The Supplier You Need</b></font>',
                ParagraphStyle('sl', fontSize=20, leading=24, textColor=ORANGE_ESVE,
                               fontName='Helvetica-Bold', alignment=TA_LEFT)
            )]]
            ht = Table(header_data, colWidths=[4*cm, 14*cm])
        else:
            ht = Table([[Paragraph(
                '<font size="20" color="#D4A017"><b>The Supplier You Need</b></font>', s_center
            )]], colWidths=[18*cm])
        ht.setStyle(TableStyle([
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW',     (0,0), (-1,-1), 2, ORANGE_ESVE),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
        ]))
        elements.append(ht)
        elements.append(Spacer(1, 0.8*cm))

        # Destinataires à droite
        societe = data.get('societe', '')
        if societe:
            elements.append(Paragraph(f'<b>{societe}</b>', s_right))
        destinataires = data.get('destinataires', [])
        for d in destinataires[:3]:
            nom      = d.get('nom', '').strip()
            fonction = d.get('fonction', '').strip()
            if nom or fonction:
                line = f'<b>{nom}</b>' if nom else ''
                if fonction:
                    line += f'{"  –  " if nom else ""}{fonction}'
                elements.append(Paragraph(line, s_right))
        elements.append(Spacer(1, 0.6*cm))

        # Objet
        elements.append(Paragraph(
            f'{T["objet_label"]} <b>{T["objet_texte"]}</b>', s_objet
        ))

        # Salutation
        elements.append(Paragraph(T['salutation'], s_bold))
        elements.append(Spacer(1, 0.2*cm))

        # Corps
        for key in ['intro', 'p1', 'p2', 'p3', 'p4']:
            elements.append(Paragraph(T[key], s_normal))

        # Texte libre additionnel
        texte_custom = data.get('texte_custom', '').strip()
        if texte_custom:
            elements.append(Paragraph(texte_custom, s_normal))

        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph(T['attente'], s_normal))
        elements.append(Spacer(1, 1.2*cm))

        # Domaines
        elements.append(HRFlowable(width='100%', thickness=1, color=ORANGE_ESVE))
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph(f'<b>{T["domaines"]}</b>', s_bold))
        elements.append(Spacer(1, 0.3*cm))

        for titre_key, texte_key in [
            ('d1_titre', 'd1_texte'),
            ('d2_titre', 'd2_texte'),
            ('d3_titre', 'd3_texte'),
            ('d4_titre', 'd4_texte'),
        ]:
            elements.append(Paragraph(T[titre_key], s_titre))
            elements.append(Paragraph(T[texte_key], s_normal))
            elements.append(Spacer(1, 0.2*cm))

        return elements

    # ── Premier build pour compter les pages ─────────────────────────────────
    buf_temp = BytesIO()
    doc_temp = SimpleDocTemplate(
        buf_temp, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2.5*cm
    )

    class PageCounter:
        count = 0
        def __call__(self, canvas, doc):
            self.count = doc.page

    pc = PageCounter()
    doc_temp.build(build_story(), onLaterPages=pc, onFirstPage=pc)
    page_counter['total'] = pc.count

    # ── Build final avec footer sur dernière page uniquement ─────────────────
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2.5*cm
    )
    doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)

    return buffer.getvalue()