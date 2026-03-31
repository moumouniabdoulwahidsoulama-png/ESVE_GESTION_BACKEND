from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, Image as RLImage, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import os

ORANGE = colors.HexColor('#D4A017')
GRIS   = colors.HexColor('#555555')


def _img(filename):
    candidates = [
        os.path.join(os.path.dirname(__file__), '..', 'static', filename),
        os.path.join(os.path.dirname(__file__), filename),
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
        'salutation': 'Madame, Monsieur,',
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
    },
    'en': {
        'objet_label': 'Subject:',
        'objet_texte': 'Service Offer — Presentation of ESVE – Ecology Smart Vision Equipement',
        'salutation': 'Dear Sir/Madam,',
        'intro': ("We are pleased to present our company, <b>ESVE – Ecology Smart Vision Equipement</b>, specialised in "
                  "the supply of high-value technical solutions for the mining, quarrying, construction and industrial sectors."),
        'p1': ("Based in Burkina Faso, ESVE's mission is to help industrial operators optimise their productivity, reduce "
               "operational costs, and comply with environmental and safety standards. Our approach is built on core values: "
               "<b>quality, responsiveness and adaptability to field realities.</b>"),
        'p2': ("To guarantee the reliability and performance of our services, ESVE works with a panel of the best local and "
               "international suppliers, rigorously selected for their expertise, innovation and compliance with international standards."),
        'p3': ("Fully aware of the technical, logistical and environmental challenges of the Burkinabe mining sector, ESVE "
               "positions itself as a trusted strategic partner, delivering robust, sustainable solutions. Thanks to local expertise, "
               "we offer tailor-made support meeting requirements for efficiency, profitability and social responsibility."),
        'p4': ("As part of the development of our activities, we request to be registered in your supplier database so that "
               "we may be consulted for any request or need related to our areas of expertise."),
        'attente': "We look forward to hearing from you and remain at your disposal for any further information.",
        'domaines': "Our main areas of expertise:",
        'd1_titre': "Supply of Ground Engaging Tools (G.E.T. / O.A.S) and Undercarriage Components (U.C / T.D.R)",
        'd1_texte': ("ESVE offers a wide range of teeth, adapters, shrouds, blades and cutting edges compatible with Caterpillar, "
                     "Komatsu, Hensley and ESCO equipment for mining, quarrying and civil engineering."),
        'd2_titre': "Supply of Mechanical Parts and Components",
        'd2_texte': ("We hold a portfolio of spare parts and mechanical components (engines, gearboxes, torque converters, "
                     "hydraulic pumps, cylinders…), new or reconditioned, for Caterpillar, Komatsu and Volvo equipment."),
        'd3_titre': "Industrial and Construction Equipment Rental",
        'd3_texte': "To meet the temporary or urgent needs of your sites: excavators, loaders, generators, compressors, etc.",
        'd4_titre': "Technical Service and Support",
        'd4_texte': ("Our qualified teams provide installation, maintenance and technical monitoring with a reactive "
                     "after-sales service close to your operating sites."),
    }
}

FOOTER = {
    'fr': ("ECOLOGY SMART VISION EQUIPEMENT  |  S/C 04 BP 398 OUAGA 04 – Secteur 42 OUAGADOUGOU  |  "
           "(+226) 05 56 25 92  |  direction@svequipement.com\n"
           "N° RIB : BF148-01001-077355324101-26  |  N° RCCM : BF-OUA-01-2025-B13-08308  |  "
           "N° IFU : 00272062K  |  Régime : RSI  |  Division fiscale : OUAGA VII"),
    'en': ("ECOLOGY SMART VISION EQUIPEMENT  |  S/C 04 BP 398 OUAGA 04 – Secteur 42 OUAGADOUGOU  |  "
           "(+226) 05 56 25 92  |  direction@svequipement.com\n"
           "RIB: BF148-01001-077355324101-26  |  RCCM: BF-OUA-01-2025-B13-08308  |  "
           "IFU: 00272062K  |  Tax regime: RSI  |  Tax division: OUAGA VII"),
}


def generer_pdf_offre(data: dict) -> bytes:
    langue = data.get('langue', 'fr')
    T      = TEXTES[langue]
    buf    = BytesIO()

    s_normal = ParagraphStyle('n',  fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=8)
    s_bold   = ParagraphStyle('b',  fontSize=10, leading=15, alignment=TA_JUSTIFY,
                               fontName='Helvetica-Bold', spaceAfter=8)
    s_right  = ParagraphStyle('r',  fontSize=9,  leading=13, alignment=TA_RIGHT, textColor=GRIS)
    s_titre  = ParagraphStyle('t',  fontSize=11, leading=14, fontName='Helvetica-Bold',
                               textColor=ORANGE, spaceAfter=6)
    s_objet  = ParagraphStyle('o',  fontSize=10, leading=14, fontName='Helvetica-Bold', spaceAfter=10)
    s_footer = ParagraphStyle('f',  fontSize=7.5, leading=11, alignment=TA_CENTER, textColor=GRIS)
    s_slogan = ParagraphStyle('sl', fontSize=22, leading=28, textColor=ORANGE,
                               fontName='Helvetica-Bold', alignment=TA_RIGHT)

    total_pages = [0]

    def draw_footer(canvas, doc):
        canvas.saveState()
        if doc.page == total_pages[0]:
            ft = Table([[Paragraph(FOOTER[langue].replace('\n', '<br/>'), s_footer)]],
                       colWidths=[18*cm])
            ft.setStyle(TableStyle([
                ('LINEABOVE',     (0,0), (-1,-1), 1.5, ORANGE),
                ('TOPPADDING',    (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            ft.wrapOn(canvas, A4[0] - 3*cm, 2.5*cm)
            ft.drawOn(canvas, 1.5*cm, 0.8*cm)
        canvas.restoreState()

    def make_story():
        els = []

        # ── EN-TÊTE : logo à gauche, slogan aligné à droite ──────────────────
        logo_p = _img('logo-esve.jpg') or _img('logo-esve.png')
        slogan = Paragraph('The Supplier You Need', s_slogan)
        if logo_p:
            hdr = Table([[RLImage(logo_p, 3.8*cm, 3.8*cm), slogan]],
                        colWidths=[4.5*cm, 13.5*cm])
        else:
            hdr = Table([[slogan]], colWidths=[18*cm])
        hdr.setStyle(TableStyle([
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',         (1,0), (1,0),   'RIGHT'),
            ('LINEBELOW',     (0,0), (-1,-1), 2.5, ORANGE),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
        ]))
        els.append(hdr)
        els.append(Spacer(1, 0.8*cm))

        # ── Destinataires ─────────────────────────────────────────────────────
        soc = (data.get('societe') or '').strip()
        if soc:
            els.append(Paragraph(f'<b>{soc}</b>', s_right))
        for d in (data.get('destinataires') or [])[:3]:
            nom = (d.get('nom') or '').strip()
            fn  = (d.get('fonction') or '').strip()
            if nom or fn:
                els.append(Paragraph(
                    (f'<b>{nom}</b>' if nom else '') + (f'  –  {fn}' if fn else ''), s_right))
        els.append(Spacer(1, 0.6*cm))

        # ── Corps de lettre ───────────────────────────────────────────────────
        els.append(Paragraph(f'{T["objet_label"]} <b>{T["objet_texte"]}</b>', s_objet))
        els.append(Paragraph(T['salutation'], s_bold))
        els.append(Spacer(1, 0.2*cm))
        for k in ['intro', 'p1', 'p2', 'p3', 'p4']:
            els.append(Paragraph(T[k], s_normal))
        custom = (data.get('texte_custom') or '').strip()
        if custom:
            els.append(Paragraph(custom, s_normal))
        els.append(Spacer(1, 0.4*cm))
        els.append(Paragraph(T['attente'], s_normal))
        els.append(Spacer(1, 1.2*cm))

        # ── Domaines ─────────────────────────────────────────────────────────
        els.append(HRFlowable(width='100%', thickness=1, color=ORANGE))
        els.append(Spacer(1, 0.4*cm))
        els.append(Paragraph(f'<b>{T["domaines"]}</b>', s_bold))
        els.append(Spacer(1, 0.3*cm))

        els.append(Paragraph(T['d1_titre'], s_titre))
        els.append(Paragraph(T['d1_texte'], s_normal))
        els.append(Spacer(1, 0.2*cm))
        els.append(Paragraph(T['d2_titre'], s_titre))
        els.append(Paragraph(T['d2_texte'], s_normal))

        # ── Grille photos produits ────────────────────────────────────────────
        prod_p = _img('esve_products.png')
        if prod_p:
            els.append(Spacer(1, 0.4*cm))
            els.append(RLImage(prod_p, width=18*cm, height=11.5*cm))
            els.append(Spacer(1, 0.5*cm))
        else:
            els.append(Spacer(1, 0.4*cm))

        els.append(Paragraph(T['d3_titre'], s_titre))
        els.append(Paragraph(T['d3_texte'], s_normal))
        els.append(Spacer(1, 0.2*cm))
        els.append(Paragraph(T['d4_titre'], s_titre))
        els.append(Paragraph(T['d4_texte'], s_normal))

        # ── Image terrain (dernière page) ─────────────────────────────────────
        field_p = _img('esve_field.png')
        if field_p:
            els.append(Spacer(1, 0.5*cm))
            tbl = Table([[RLImage(field_p, width=18*cm, height=9*cm)]], colWidths=[18*cm])
            tbl.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
            els.append(tbl)

        return els

    # Pré-build pour compter les pages
    tmp = BytesIO()
    dtmp = SimpleDocTemplate(tmp, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                              topMargin=1.5*cm, bottomMargin=2.5*cm)
    class PC:
        count = 0
        def __call__(self, c, d): self.count = d.page
    pc = PC()
    dtmp.build(make_story(), onFirstPage=pc, onLaterPages=pc)
    total_pages[0] = pc.count

    # Build final
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                             topMargin=1.5*cm, bottomMargin=2.5*cm)
    doc.build(make_story(), onFirstPage=draw_footer, onLaterPages=draw_footer)
    return buf.getvalue()