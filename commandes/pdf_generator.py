from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO
import os

# Couleurs — jaune/or ESVE
ORANGE_ESVE  = colors.HexColor('#D4A017')
DARK_ESVE    = colors.HexColor('#1A1A2E')
GRIS_CLAIR   = colors.HexColor('#F5F5F5')
BLANC        = colors.white
ROUGE        = colors.HexColor('#B71C1C')
BLEU         = colors.HexColor('#1565C0')
VERT         = colors.HexColor('#1B5E20')


def get_logo_path():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo-esve.jpg')
    return logo_path if os.path.exists(logo_path) else None


def nombre_en_lettres(montant):
    try:
        from num2words import num2words
        return num2words(int(montant), lang='fr').capitalize() + " Francs CFA"
    except Exception:
        return f"{int(montant):,} Francs CFA".replace(',', ' ')


def build_header(style_normal, style_left):
    """Header sans sous-titre — le logo contient déjà le nom de l'entreprise."""
    logo_path = get_logo_path()
    style_slogan = ParagraphStyle(
        'slogan', fontSize=22, leading=26,
        textColor=ORANGE_ESVE, fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    if logo_path:
        logo = RLImage(logo_path, width=3.5*cm, height=3.5*cm)
        header_data = [[logo, Paragraph(
            '<font size="22" color="#D4A017"><b>The Supplier You Need</b></font>',
            style_slogan
        )]]
        col_widths = [4*cm, 14*cm]
    else:
        header_data = [[Paragraph(
            '<font size="22" color="#D4A017"><b>The Supplier You Need</b></font>',
            style_slogan
        )]]
        col_widths = [18*cm]

    t = Table(header_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW',     (0,0), (-1,-1), 2, ORANGE_ESVE),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
    ]))
    return t


def build_footer(style_normal, style_right):
    footer_data = [[
        Paragraph(
            '<font size="8" color="#777777">'
            '<b>ECOLOGY SMART VISION EQUIPEMENT</b><br/>'
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


# ─────────────────────────────────────────────
#  BON DE COMMANDE
# ─────────────────────────────────────────────
def generer_pdf_bon_commande(bon):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=3*cm
    )

    style_normal = ParagraphStyle('normal', fontSize=9,  leading=13)
    style_right  = ParagraphStyle('right',  fontSize=9,  leading=13, alignment=TA_RIGHT)
    style_left   = ParagraphStyle('left',   fontSize=9,  leading=13, alignment=TA_LEFT)
    style_center = ParagraphStyle('center', fontSize=9,  leading=13, alignment=TA_CENTER)
    style_title  = ParagraphStyle('title',  fontSize=18, leading=22,
                                  textColor=DARK_ESVE, alignment=TA_CENTER,
                                  fontName='Helvetica-Bold')
    style_numero = ParagraphStyle('numero', fontSize=13, leading=16,
                                  textColor=ORANGE_ESVE, alignment=TA_CENTER,
                                  fontName='Helvetica-Bold')

    def on_page(canvas, doc):
        canvas.saveState()
        footer = build_footer(style_normal, style_right)
        w, h = A4
        footer.wrapOn(canvas, w - 3*cm, 2*cm)
        footer.drawOn(canvas, 1.5*cm, 1*cm)
        canvas.restoreState()

    elements = []

    # HEADER
    elements.append(build_header(style_normal, style_left))
    elements.append(Spacer(1, 0.5*cm))

    # TITRE
    elements.append(Paragraph('<u>BON DE COMMANDE</u>', style_title))
    elements.append(Paragraph(f'N° : {bon.numero}', style_numero))
    elements.append(Spacer(1, 0.5*cm))

    # FOURNISSEUR + DÉTAILS
    fournisseur_info = f'<b>{bon.fournisseur_nom}</b><br/>'
    if bon.fournisseur_adresse:          fournisseur_info += f'{bon.fournisseur_adresse}<br/>'
    if bon.fournisseur_ifu:              fournisseur_info += f'IFU : {bon.fournisseur_ifu}<br/>'
    if bon.fournisseur_rccm:             fournisseur_info += f'RCCM : {bon.fournisseur_rccm}<br/>'
    if bon.fournisseur_division_fiscale: fournisseur_info += f'Division Fiscale : {bon.fournisseur_division_fiscale}<br/>'
    if bon.fournisseur_regime:           fournisseur_info += f'Régime fiscal : {bon.fournisseur_regime}<br/>'
    if bon.fournisseur_tel:              fournisseur_info += f'Tél : {bon.fournisseur_tel}'

    details_info = ''
    if bon.ref_proforma_fournisseur:
        details_info += f'<b>Facture Proforma N°</b> {bon.ref_proforma_fournisseur}<br/>'
    if bon.date_proforma_fournisseur:
        details_info += f'<b>Date :</b> {bon.date_proforma_fournisseur.strftime("%d/%m/%Y")}<br/>'
    details_info += f'<b>Date commande :</b> {bon.date_commande.strftime("%d/%m/%Y")}<br/>'
    if bon.termes_paiement:
        details_info += f'<b>Termes de paiement :</b> {bon.termes_paiement}<br/>'
    if bon.termes_livraison:
        details_info += f'<b>Termes de livraison :</b> {bon.termes_livraison}'

    info_data = [[
        Paragraph('<font color="#999999"><i>Fournisseur :</i></font><br/>' + fournisseur_info, style_normal),
        Paragraph('<font color="#999999"><i>Détails de l\'offre :</i></font><br/>' + details_info, style_normal),
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

    # TABLEAU LIGNES — sans lignes vides
    COL_WIDTHS = [4.2*cm, 2*cm, 2.3*cm, 2.5*cm, 2.0*cm, 2.5*cm, 2.5*cm]

    style_header_col = ParagraphStyle(
        'header_col', fontSize=8, leading=10,
        textColor=BLANC, fontName='Helvetica-Bold',
        alignment=TA_CENTER, wordWrap='LTR'
    )

    delais_label = 'Délais DDP OUAGA' if bon.termes_livraison and 'DDP' in bon.termes_livraison else 'Délais'

    lignes_data = [[
        Paragraph('Description',          style_header_col),
        Paragraph('Référence client',      style_header_col),
        Paragraph('Référence fournisseur', style_header_col),
        Paragraph('Prix unitaire HT XOF',  style_header_col),
        Paragraph('Quantité',              style_header_col),
        Paragraph('Total HT XOF',         style_header_col),
        Paragraph(delais_label,            style_header_col),
    ]]

    for ligne in bon.lignes.all():
        lignes_data.append([
            Paragraph(ligne.description or '', style_normal),
            Paragraph(ligne.reference_client or '', style_normal),
            Paragraph(ligne.reference_fournisseur or '', style_normal),
            Paragraph(f'{int(ligne.prix_unitaire_ht):,}'.replace(',', ' '), style_right),
            Paragraph(f'{ligne.quantite:.2f}', style_right),
            Paragraph(f'{int(ligne.total_ht):,}'.replace(',', ' '), style_right),
            Paragraph(ligne.delais or '', style_normal),
        ])

    # Pas de lignes vides pour le bon de commande

    lignes_table = Table(lignes_data, colWidths=COL_WIDTHS)
    lignes_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), ORANGE_ESVE),
        ('TEXTCOLOR',      (0,0), (-1,0), BLANC),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BLANC, GRIS_CLAIR]),
        ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#E0E0E0')),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',     (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
        ('LEFTPADDING',    (0,0), (-1,-1), 4),
        ('ALIGN',          (0,0), (-1,0), 'CENTER'),
    ]))
    elements.append(lignes_table)
    elements.append(Spacer(1, 0.3*cm))

    # TOTAUX — utilise getattr pour éviter les crashs si champs manquants
    total_ht  = getattr(bon, 'total_ht',  0) or 0
    total_net = getattr(bon, 'total_net', 0) or 0

    totaux_data = [['Montant HT', f"{int(total_ht):,} XOF".replace(',', ' ')]]

    remise_pct    = getattr(bon, 'remise_pct', 0) or 0
    montant_remise = getattr(bon, 'montant_remise', 0) or 0
    if getattr(bon, 'appliquer_remise', False) and montant_remise > 0:
        totaux_data.append([
            f'Remise ({remise_pct}%)',
            f"- {int(montant_remise):,} XOF".replace(',', ' ')
        ])

    tva_18pct = getattr(bon, 'tva_18pct', 0) or 0
    if getattr(bon, 'appliquer_tva', False) and tva_18pct > 0:
        totaux_data.append(['TVA 18%', f"{int(tva_18pct):,} XOF".replace(',', ' ')])

    retenue_5pct = getattr(bon, 'retenue_5pct', 0) or 0
    if getattr(bon, 'appliquer_retenue', False) and retenue_5pct > 0:
        totaux_data.append(['Retenue (5%)', f"- {int(retenue_5pct):,} XOF".replace(',', ' ')])

    bic_2pct = getattr(bon, 'bic_2pct', 0) or 0
    if getattr(bon, 'appliquer_bic', False) and bic_2pct > 0:
        totaux_data.append(['BIC 2%', f"- {int(bic_2pct):,} XOF".replace(',', ' ')])

    montant_transport = getattr(bon, 'montant_transport', 0) or 0
    if getattr(bon, 'appliquer_transport', False) and montant_transport > 0:
        totaux_data.append(['Transport', f"{int(montant_transport):,} XOF".replace(',', ' ')])

    totaux_data.append(['Total TTC', f"{int(total_net):,} XOF".replace(',', ' ')])

    totaux_table = Table(totaux_data, colWidths=[5*cm, 4*cm], hAlign='RIGHT')
    totaux_style = [
        ('FONTSIZE',       (0,0), (-1,-1), 9),
        ('GRID',           (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
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
    for i, row in enumerate(totaux_data):
        if 'Remise'    in row[0]: totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), ROUGE))
        if 'TVA'       in row[0]: totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), BLEU))
        if 'Retenue'   in row[0] or 'BIC' in row[0]: totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), ROUGE))
        if 'Transport' in row[0]: totaux_style.append(('TEXTCOLOR', (0,i), (-1,i), VERT))

    totaux_table.setStyle(TableStyle(totaux_style))
    elements.append(totaux_table)
    elements.append(Spacer(1, 0.4*cm))

    # MONTANT EN LETTRES
    lettres_table = Table([[
        Paragraph(
            f'<b>Arrêté le présent Bon de commande à la somme :</b> '
            f'<i>{nombre_en_lettres(total_net)}</i>',
            style_normal)
    ]], colWidths=[18*cm])
    lettres_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#FFF3E0')),
        ('LINEAFTER',     (0,0), (0,-1), 3, ORANGE_ESVE),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(lettres_table)

    if bon.notes:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f'<i><b>Notes :</b> {bon.notes}</i>', style_normal))

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"{bon.numero}.pdf"
    if bon.pdf_file:
        bon.pdf_file.delete(save=False)
    bon.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    return bon.pdf_file