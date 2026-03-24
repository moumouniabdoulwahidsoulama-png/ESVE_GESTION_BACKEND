from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO
import os

ORANGE_ESVE = colors.HexColor('#D4830A')
DARK_ESVE   = colors.HexColor('#1A1A2E')
GRIS_CLAIR  = colors.HexColor('#F5F5F5')
BLANC       = colors.white
ROUGE       = colors.HexColor('#B71C1C')
BLEU        = colors.HexColor('#1565C0')


def get_logo_path():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo-esve.jpg')
    return logo_path if os.path.exists(logo_path) else None


def nombre_en_lettres(montant):
    try:
        from num2words import num2words
        return num2words(int(montant), lang='fr').capitalize() + " Francs CFA"
    except Exception:
        return f"{int(montant):,} Francs CFA".replace(',', ' ')


def build_header(style_normal, style_right):
    logo_path    = get_logo_path()
    company_info = Paragraph(
        '<font size="8" color="#555555">'
        'S/C 04 BP 398 OUAGA 04<br/>'
        'Secteur 42 OUAGADOUGOU<br/>'
        'Tél : (+226) 05 56 25 92<br/>'
        'direction@svequipement.com<br/><br/>'
        'N° RCCM : BF-OUA-01-2025-B13-08308<br/>'
        'N° IFU : 00272062K<br/>'
        'N° RIB : BF148-01001-077355324101-26'
        '</font>', style_right)

    company_name = Paragraph(
        '<font size="18" color="#D4830A"><b>ESVE</b></font><br/>'
        '<font size="9" color="#555555">Ecology Smart Vision Equipement</font><br/>'
        '<font size="8" color="#D4830A"><b>The Supplier You Need</b></font>',
        style_normal)

    if logo_path:
        logo        = RLImage(logo_path, width=2.2*cm, height=2.2*cm)
        header_data = [[logo, company_name, company_info]]
        col_widths  = [2.5*cm, 6.5*cm, 9*cm]
    else:
        header_data = [[company_name, company_info]]
        col_widths  = [9*cm, 9*cm]

    t = Table(header_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW',     (0,0), (-1,-1), 2, ORANGE_ESVE),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    return t


def build_footer(style_normal, style_right):
    footer_data = [[
        Paragraph(
            '<font size="8" color="#777777">'
            'ECOLOGY SMART VISION EQUIPEMENT<br/>'
            'S/C 04 BP 398 OUAGA 04 — Secteur 42 OUAGADOUGOU<br/>'
            '(+226) 05 56 25 92 — direction@svequipement.com'
            '</font>', style_normal),
        Paragraph(
            '<font size="8" color="#777777">'
            'N° RIB : BF148-01001-077355324101-26<br/>'
            'N° RCCM : BF-OUA-01-2025-B13-08308<br/>'
            'N° IFU : 00272062K — Régime : RSI'
            '</font>', style_right),
    ]]
    t = Table(footer_data, colWidths=[9*cm, 9*cm])
    t.setStyle(TableStyle([
        ('LINEABOVE',  (0,0), (-1,-1), 1.5, ORANGE_ESVE),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
    ]))
    return t


def generer_pdf_facture(facture):
    buffer = BytesIO()

    # Marges avec espace pour footer
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=3*cm  # ← espace footer
    )

    style_normal = ParagraphStyle('normal', fontSize=9,  leading=13)
    style_right  = ParagraphStyle('right',  fontSize=9,  leading=13, alignment=TA_RIGHT)
    style_title  = ParagraphStyle('title',  fontSize=18, leading=22,
                                  textColor=DARK_ESVE, alignment=TA_CENTER,
                                  fontName='Helvetica-Bold')
    style_numero = ParagraphStyle('numero', fontSize=13, leading=16,
                                  textColor=ORANGE_ESVE, alignment=TA_CENTER,
                                  fontName='Helvetica-Bold')

    # Footer fixe en bas de page
    def on_page(canvas, doc):
        canvas.saveState()
        footer = build_footer(style_normal, style_right)
        w, h = A4
        footer.wrapOn(canvas, w - 3*cm, 2*cm)
        footer.drawOn(canvas, 1.5*cm, 1*cm)
        canvas.restoreState()

    elements = []

    # HEADER
    elements.append(build_header(style_normal, style_right))
    elements.append(Spacer(1, 0.5*cm))

    # TITRE
    type_label = "FACTURE PRO-FORMA" if facture.type_doc == 'PROFORMA' else "FACTURE"
    elements.append(Paragraph(f'<u>{type_label}</u>', style_title))
    elements.append(Paragraph(f'N° : {facture.numero}', style_numero))
    elements.append(Spacer(1, 0.5*cm))

    # CLIENT + DATE
    client = facture.client
    client_info = f'<b>{client.nom_entreprise}</b><br/>'
    if client.adresse:       client_info += f'{client.adresse}<br/>'
    if client.telephone:     client_info += f'Tél : {client.telephone}<br/>'
    if client.rccm:          client_info += f'N° RCCM : {client.rccm}<br/>'
    if client.ifu:           client_info += f'N° IFU : {client.ifu}<br/>'
    if client.regime_imposition:  client_info += f"Régime d'Imposition : {client.regime_imposition}<br/>"
    if client.division_fiscale:   client_info += f"Division fiscale : {client.division_fiscale}"

    date_info = (
        f'<b>Date de la facture :</b> {facture.date_creation.strftime("%d/%m/%Y")}<br/>'
        f'<b>Validité :</b> {facture.validite_jours} Jours'
    )
    if facture.proforma_origine:
        date_info += f'<br/><b>Proforma origine :</b> {facture.proforma_origine.numero}'

    info_data = [[
        Paragraph('<font color="#999999"><i>Client :</i></font><br/>' + client_info, style_normal),
        Paragraph('<font color="#999999"><i>Détails de l\'offre :</i></font><br/>' + date_info, style_normal),
    ]]
    info_table = Table(info_data, colWidths=[9*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('BOX',           (0,0), (0,0), 0.5, colors.HexColor('#E0E0E0')),
        ('BOX',           (1,0), (1,0), 0.5, colors.HexColor('#E0E0E0')),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    # TABLEAU LIGNES
    lignes_data = [[
        Paragraph('<b>Description</b>',       style_normal),
        Paragraph('<b>Réf. client</b>',        style_normal),
        Paragraph('<b>Réf. fournisseur</b>',   style_normal),
        Paragraph('<b>Prix unitaire HTVA</b>', style_normal),
        Paragraph('<b>Quantité</b>',           style_normal),
        Paragraph('<b>Total HTVA XOF</b>',     style_normal),
        Paragraph('<b>Délais</b>',             style_normal),
    ]]

    for ligne in facture.lignes.all():
        lignes_data.append([
            Paragraph(ligne.description, style_normal),
            Paragraph(ligne.reference_client or '', style_normal),
            Paragraph(ligne.reference_fournisseur or '', style_normal),
            Paragraph(f'{int(ligne.prix_unitaire_ht):,}'.replace(',', ' '), style_right),
            Paragraph(str(ligne.quantite), style_right),
            Paragraph(f'{int(ligne.total_ht):,}'.replace(',', ' '), style_right),
            Paragraph(ligne.delais or '', style_normal),
        ])

    lignes_table = Table(
        lignes_data,
        colWidths=[5*cm, 2.3*cm, 2.3*cm, 2.5*cm, 1.5*cm, 2.5*cm, 1.9*cm]
    )
    lignes_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), ORANGE_ESVE),
        ('TEXTCOLOR',      (0,0), (-1,0), BLANC),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BLANC, GRIS_CLAIR]),
        ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#E0E0E0')),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',     (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 5),
        ('LEFTPADDING',    (0,0), (-1,-1), 5),
    ]))
    elements.append(lignes_table)
    elements.append(Spacer(1, 0.4*cm))

    # TOTAUX — uniquement les champs cochés
    totaux_data = [
        ['Montant HTVA', f"{int(facture.total_ht_brut):,} XOF".replace(',', ' ')],
    ]

    if facture.appliquer_remise and facture.remise_pct > 0:
        totaux_data.append([
            f'Remise ({facture.remise_pct}%)',
            f"- {int(facture.montant_remise):,} XOF".replace(',', ' ')
        ])
        totaux_data.append([
            'Montant HTVA Net',
            f"{int(facture.total_ht):,} XOF".replace(',', ' ')
        ])

    if facture.appliquer_tva and facture.tva_18pct > 0:
        totaux_data.append([
            'TVA (18%)',
            f"+ {int(facture.tva_18pct):,} XOF".replace(',', ' ')
        ])

    if facture.appliquer_retenue and facture.retenue_5pct > 0:
        totaux_data.append([
            'Retenue (5%)',
            f"- {int(facture.retenue_5pct):,} XOF".replace(',', ' ')
        ])

    if facture.appliquer_bic and facture.bic_2pct > 0:
        totaux_data.append([
            'BIC (2%)',
            f"- {int(facture.bic_2pct):,} XOF".replace(',', ' ')
        ])

    totaux_data.append([
        'TOTAL NET',
        f"{int(facture.total_net):,} XOF".replace(',', ' ')
    ])

    totaux_table = Table(totaux_data, colWidths=[5*cm, 4*cm], hAlign='RIGHT')
    totaux_style = [
        ('FONTSIZE',       (0,0), (-1,-1), 9),
        ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#E0E0E0')),
        ('LEFTPADDING',    (0,0), (-1,-1), 8),
        ('RIGHTPADDING',   (0,0), (-1,-1), 8),
        ('TOPPADDING',     (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
        ('ALIGN',          (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME',       (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND',     (0,-1), (-1,-1), ORANGE_ESVE),
        ('TEXTCOLOR',      (0,-1), (-1,-1), BLANC),
        ('FONTSIZE',       (0,-1), (-1,-1), 11),
    ]

    # Couleurs TVA en bleu
    for i, row in enumerate(totaux_data):
        if 'TVA' in row[0]:
            totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), BLEU))
        if 'Retenue' in row[0] or 'BIC' in row[0]:
            totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), ROUGE))

    totaux_table.setStyle(TableStyle(totaux_style))
    elements.append(totaux_table)
    elements.append(Spacer(1, 0.4*cm))

    # MONTANT EN LETTRES
    lettres_data = [[
        Paragraph(
            f'<b>Arrêté la présente facture à la somme de :</b> '
            f'<i>{nombre_en_lettres(facture.total_net)}</i>',
            style_normal)
    ]]
    lettres_table = Table(lettres_data, colWidths=[18*cm])
    lettres_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#FFF3E0')),
        ('LINEAFTER',     (0,0), (0,-1), 3, ORANGE_ESVE),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(lettres_table)

    if facture.notes:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f'<i><b>Notes :</b> {facture.notes}</i>', style_normal))

    # BUILD avec footer sur chaque page
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"{facture.numero}.pdf"
    if facture.pdf_file:
        facture.pdf_file.delete(save=False)
    facture.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    return facture.pdf_file