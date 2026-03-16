from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.core.files.base import ContentFile
from io import BytesIO

# Couleurs ESVE
ORANGE_ESVE = colors.HexColor('#D4830A')
DARK_ESVE   = colors.HexColor('#1A1A2E')
GRIS_CLAIR  = colors.HexColor('#F5F5F5')
BLANC       = colors.white
ROUGE       = colors.HexColor('#B71C1C')
BLEU        = colors.HexColor('#1565C0')


def nombre_en_lettres(montant):
    try:
        from num2words import num2words
        entier = int(montant)
        return num2words(entier, lang='fr').capitalize() + " Francs CFA"
    except Exception:
        return f"{int(montant):,} Francs CFA".replace(',', ' ')


def generer_pdf_bon_commande(bon):
    buffer  = BytesIO()
    doc     = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm,   bottomMargin=1.5*cm
    )
    styles   = getSampleStyleSheet()
    elements = []

    style_normal = ParagraphStyle('normal', fontSize=9,  leading=13)
    style_right  = ParagraphStyle('right',  fontSize=9,  leading=13, alignment=TA_RIGHT)
    style_title  = ParagraphStyle('title',  fontSize=18, leading=22, textColor=DARK_ESVE,   alignment=TA_CENTER, fontName='Helvetica-Bold')
    style_numero = ParagraphStyle('numero', fontSize=13, leading=16, textColor=ORANGE_ESVE, alignment=TA_CENTER, fontName='Helvetica-Bold')

    # ===== HEADER =====
    header_data = [[
        Paragraph(
            '<font size="18" color="#D4830A"><b>ESVE</b></font><br/>'
            '<font size="9" color="#555555">Ecology Smart Vision Equipement</font><br/>'
            '<font size="8" color="#D4830A"><b>The Supplier You Need</b></font>',
            style_normal
        ),
        Paragraph(
            '<font size="8" color="#555555">'
            'S/C 04 BP 398 OUAGA 04<br/>'
            'Secteur 42 OUAGADOUGOU<br/>'
            'Tél : (+226) 05 56 25 92<br/>'
            'direction@svequipement.com<br/><br/>'
            'N° RCCM : BF-OUA-01-2025-B13-08308<br/>'
            'N° IFU : 00272062K<br/>'
            'N° RIB : BF148-01001-077355324101-26'
            '</font>',
            style_right
        ),
    ]]
    header_table = Table(header_data, colWidths=[9*cm, 9*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW',     (0,0), (-1,-1), 2, ORANGE_ESVE),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))

    # ===== TITRE =====
    elements.append(Paragraph('<u>BON DE COMMANDE FOURNISSEUR</u>', style_title))
    elements.append(Paragraph(f'N° : {bon.numero}', style_numero))
    elements.append(Spacer(1, 0.5*cm))

    # ===== FOURNISSEUR + DATE =====
    fournisseur_info = (
        f'<b>{bon.fournisseur_nom}</b><br/>'
        + (f'{bon.fournisseur_adresse}<br/>'  if bon.fournisseur_adresse else '')
        + (f'Tél : {bon.fournisseur_tel}<br/>' if bon.fournisseur_tel    else '')
        + (f'Email : {bon.fournisseur_email}'  if bon.fournisseur_email  else '')
    )
    date_info = (
        f'<b>Date de commande :</b> {bon.date_commande.strftime("%d/%m/%Y")}<br/>'
        f'<b>Statut :</b> {bon.get_statut_display()}<br/>'
        + (f'<b>Livraison prévue :</b> {bon.date_livraison_prev.strftime("%d/%m/%Y")}' if bon.date_livraison_prev else '')
    )

    info_data = [[
        Paragraph('<font color="#999999"><i>Fournisseur :</i></font><br/>' + fournisseur_info, style_normal),
        Paragraph('<font color="#999999"><i>Détails :</i></font><br/>' + date_info, style_normal),
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

    # ===== OBJET =====
    if bon.objet:
        objet_data = [[Paragraph(f'<b>Objet :</b> {bon.objet}', style_normal)]]
        objet_table = Table(objet_data, colWidths=[18*cm])
        objet_table.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), GRIS_CLAIR),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(objet_table)
        elements.append(Spacer(1, 0.3*cm))

    # ===== TABLEAU DES LIGNES =====
    lignes_data = [[
        Paragraph('<b>Description</b>',      style_normal),
        Paragraph('<b>Référence</b>',         style_normal),
        Paragraph('<b>Unité</b>',             style_normal),
        Paragraph('<b>Prix unitaire HT</b>',  style_normal),
        Paragraph('<b>Quantité</b>',          style_normal),
        Paragraph('<b>Total HT XOF</b>',      style_normal),
    ]]

    for ligne in bon.lignes.all():
        lignes_data.append([
            Paragraph(ligne.description,                                          style_normal),
            Paragraph(ligne.reference or '',                                      style_normal),
            Paragraph(ligne.unite or '',                                          style_normal),
            Paragraph(f'{int(ligne.prix_unitaire_ht):,}'.replace(',', ' '),       style_right),
            Paragraph(str(ligne.quantite),                                        style_right),
            Paragraph(f'{int(ligne.total_ht):,}'.replace(',', ' '),              style_right),
        ])

    lignes_table = Table(lignes_data, colWidths=[6*cm, 2.5*cm, 1.5*cm, 2.8*cm, 2*cm, 3.2*cm])
    lignes_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), DARK_ESVE),
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

    # ===== TOTAUX =====
    totaux_data = [
        ['Montant HT',  f"{int(bon.total_ht):,} XOF".replace(',', ' ')],
        ['Retenue (5%)', f"- {int(bon.retenue_5pct):,} XOF".replace(',', ' ')],
        ['BIC (2%)',     f"- {int(bon.bic_2pct):,} XOF".replace(',', ' ')],
        ['TOTAL NET',   f"{int(bon.total_net):,} XOF".replace(',', ' ')],
    ]
    
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
    for label in ['Retenue', 'BIC']:
        idx = next(i for i, r in enumerate(totaux_data) if label in r[0])
        totaux_style.append(('TEXTCOLOR', (0, idx), (-1, idx), ROUGE))

    totaux_table.setStyle(TableStyle(totaux_style))
    elements.append(totaux_table)
    elements.append(Spacer(1, 0.4*cm))

    # ===== MONTANT EN LETTRES =====
    lettres_data = [[
        Paragraph(
            f'<b>Arrêté le présent bon de commande à la somme de :</b> '
            f'<i>{nombre_en_lettres(bon.total_net)}</i>',
            style_normal
        )
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

    # ===== NOTES =====
    if bon.notes:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f'<i><b>Notes :</b> {bon.notes}</i>', style_normal))

    # ===== FOOTER =====
    elements.append(Spacer(1, 1*cm))
    footer_data = [[
        Paragraph(
            '<font size="8" color="#777777">'
            'ECOLOGY SMART VISION EQUIPEMENT<br/>'
            'S/C 04 BP 398 OUAGA 04 — Secteur 42 OUAGADOUGOU<br/>'
            '(+226) 05 56 25 92 — direction@svequipement.com'
            '</font>',
            style_normal
        ),
        Paragraph(
            '<font size="8" color="#777777">'
            'N° RIB : BF148-01001-077355324101-26<br/>'
            'N° RCCM : BF-OUA-01-2025-B13-08308<br/>'
            'N° IFU : 00272062K — Régime : RSI'
            '</font>',
            style_right
        ),
    ]]
    footer_table = Table(footer_data, colWidths=[9*cm, 9*cm])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE',  (0,0), (-1,-1), 1.5, ORANGE_ESVE),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(footer_table)

    # ===== GÉNÉRER =====
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"{bon.numero}.pdf"
    if bon.pdf_file:
        bon.pdf_file.delete(save=False)

    bon.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    return bon.pdf_file