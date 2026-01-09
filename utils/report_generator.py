"""
Report Generator - Tạo báo cáo và hóa đơn bằng ReportLab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Đường dẫn thư mục reports
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

# Tạo thư mục reports nếu chưa tồn tại
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# Đăng ký font tiếng Việt (sử dụng font mặc định nếu không có)
try:
    # Thử đăng ký font Arial Unicode MS (có sẵn trên Windows)
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
    FONT_NAME = 'Arial'
    FONT_BOLD = 'ArialBold'
except:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'


def create_styles():
    """Tạo các style cho báo cáo"""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontName=FONT_BOLD,
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=20
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        fontName=FONT_NAME,
        fontSize=12,
        alignment=1,
        spaceAfter=10
    ))
    
    # Normal style
    styles.add(ParagraphStyle(
        name='CustomNormal',
        fontName=FONT_NAME,
        fontSize=10,
        alignment=0,
        spaceAfter=6
    ))
    
    # Bold style
    styles.add(ParagraphStyle(
        name='CustomBold',
        fontName=FONT_BOLD,
        fontSize=10,
        alignment=0,
        spaceAfter=6
    ))
    
    return styles


def generate_borrow_receipt(borrow_data: dict, output_path: str = None) -> str:
    """
    Tạo hóa đơn mượn sách
    
    Args:
        borrow_data: Thông tin phiếu mượn
        output_path: Đường dẫn file output (tùy chọn)
    
    Returns:
        Đường dẫn file PDF đã tạo
    """
    if output_path is None:
        filename = f"phieu_muon_{borrow_data['ma_phieu']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = create_styles()
    elements = []
    
    # Tiêu đề
    elements.append(Paragraph("THU VIEN SO", styles['CustomTitle']))
    elements.append(Paragraph("PHIEU MUON SACH", styles['CustomTitle']))
    elements.append(Spacer(1, 20))
    
    # Thông tin phiếu
    elements.append(Paragraph(f"<b>Ma phieu:</b> {borrow_data.get('ma_phieu', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"<b>Ngay muon:</b> {borrow_data.get('ngay_muon', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"<b>Ngay hen tra:</b> {borrow_data.get('ngay_hen_tra', 'N/A')}", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Thông tin độc giả
    elements.append(Paragraph("<b>THONG TIN DOC GIA</b>", styles['CustomBold']))
    elements.append(Paragraph(f"Ma doc gia: {borrow_data.get('ma_doc_gia', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"Ho ten: {borrow_data.get('ten_doc_gia', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"Dia chi: {borrow_data.get('dia_chi', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"So dien thoai: {borrow_data.get('so_dt', 'N/A')}", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Thông tin sách
    elements.append(Paragraph("<b>THONG TIN SACH</b>", styles['CustomBold']))
    
    book_data = [
        ['STT', 'Tieu de', 'Tac gia', 'The loai'],
        ['1', borrow_data.get('tieu_de', 'N/A'), 
         borrow_data.get('tac_gia', 'N/A'),
         borrow_data.get('ten_the_loai', 'N/A')]
    ]
    
    book_table = Table(book_data, colWidths=[1.5*cm, 8*cm, 4*cm, 3*cm])
    book_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(book_table)
    elements.append(Spacer(1, 20))
    
    # Nhân viên xử lý
    elements.append(Paragraph(f"<b>Nhan vien xu ly:</b> {borrow_data.get('ten_nhan_vien', 'N/A')} ({borrow_data.get('ma_nhan_vien', 'N/A')})", styles['CustomNormal']))
    elements.append(Spacer(1, 30))
    
    # Chữ ký
    signature_data = [
        ['Doc gia', 'Nhan vien'],
        ['(Ky va ghi ro ho ten)', '(Ky va ghi ro ho ten)'],
        ['', ''],
        ['', ''],
        ['', ''],
    ]
    
    sig_table = Table(signature_data, colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 1), (-1, 1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
    ]))
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    return output_path


def generate_return_receipt(borrow_data: dict, output_path: str = None) -> str:
    """
    Tạo hóa đơn trả sách
    
    Args:
        borrow_data: Thông tin phiếu mượn/trả
        output_path: Đường dẫn file output (tùy chọn)
    
    Returns:
        Đường dẫn file PDF đã tạo
    """
    if output_path is None:
        filename = f"phieu_tra_{borrow_data['ma_phieu']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = create_styles()
    elements = []
    
    # Tiêu đề
    elements.append(Paragraph("THU VIEN SO", styles['CustomTitle']))
    elements.append(Paragraph("PHIEU TRA SACH", styles['CustomTitle']))
    elements.append(Spacer(1, 20))
    
    # Thông tin phiếu
    elements.append(Paragraph(f"<b>Ma phieu:</b> {borrow_data.get('ma_phieu', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"<b>Ngay muon:</b> {borrow_data.get('ngay_muon', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"<b>Ngay hen tra:</b> {borrow_data.get('ngay_hen_tra', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"<b>Ngay tra thuc te:</b> {borrow_data.get('ngay_tra_thuc', datetime.now().strftime('%Y-%m-%d'))}", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Thông tin độc giả
    elements.append(Paragraph("<b>THONG TIN DOC GIA</b>", styles['CustomBold']))
    elements.append(Paragraph(f"Ma doc gia: {borrow_data.get('ma_doc_gia', 'N/A')}", styles['CustomNormal']))
    elements.append(Paragraph(f"Ho ten: {borrow_data.get('ten_doc_gia', 'N/A')}", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Thông tin sách
    elements.append(Paragraph("<b>THONG TIN SACH</b>", styles['CustomBold']))
    
    book_data = [
        ['STT', 'Tieu de', 'Tac gia'],
        ['1', borrow_data.get('tieu_de', 'N/A'), borrow_data.get('tac_gia', 'N/A')]
    ]
    
    book_table = Table(book_data, colWidths=[1.5*cm, 10*cm, 5*cm])
    book_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(book_table)
    elements.append(Spacer(1, 20))
    
    # Tiền phạt
    tien_phat = borrow_data.get('tien_phat', 0)
    if tien_phat > 0:
        elements.append(Paragraph(f"<b>TIEN PHAT QUA HAN: {tien_phat:,.0f} VND</b>", 
                                 ParagraphStyle(name='Fine', fontName=FONT_BOLD, 
                                               fontSize=12, textColor=colors.red)))
    else:
        elements.append(Paragraph("<b>TIEN PHAT: 0 VND (Tra dung han)</b>", styles['CustomBold']))
    
    elements.append(Spacer(1, 20))
    
    # Nhân viên xử lý
    elements.append(Paragraph(f"<b>Nhan vien xu ly:</b> {borrow_data.get('ten_nhan_vien', 'N/A')}", styles['CustomNormal']))
    elements.append(Spacer(1, 30))
    
    # Chữ ký
    signature_data = [
        ['Doc gia', 'Nhan vien'],
        ['(Ky va ghi ro ho ten)', '(Ky va ghi ro ho ten)'],
        ['', ''],
        ['', ''],
    ]
    
    sig_table = Table(signature_data, colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    return output_path


def generate_book_statistics_report(stats: dict, output_path: str = None) -> str:
    """
    Tạo báo cáo thống kê sách
    
    Args:
        stats: Dữ liệu thống kê
        output_path: Đường dẫn file output (tùy chọn)
    
    Returns:
        Đường dẫn file PDF đã tạo
    """
    if output_path is None:
        filename = f"thong_ke_sach_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = create_styles()
    elements = []
    
    # Tiêu đề
    elements.append(Paragraph("THU VIEN SO", styles['CustomTitle']))
    elements.append(Paragraph("BAO CAO THONG KE SACH", styles['CustomTitle']))
    elements.append(Paragraph(f"Ngay lap: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # Tổng quan
    elements.append(Paragraph("<b>1. TONG QUAN</b>", styles['CustomBold']))
    elements.append(Paragraph(f"Tong so sach: {stats.get('total_books', 0)} cuon", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Theo trạng thái
    elements.append(Paragraph("<b>2. SACH THEO TRANG THAI</b>", styles['CustomBold']))
    by_status = stats.get('by_status', {})
    status_data = [['Trang thai', 'So luong']]
    status_map = {'CO_SAN': 'Co san', 'DA_MUON': 'Da muon', 'HONG': 'Hong', 'MAT': 'Mat'}
    for status, count in by_status.items():
        status_data.append([status_map.get(status, status), str(count)])
    
    if len(status_data) > 1:
        status_table = Table(status_data, colWidths=[8*cm, 4*cm])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ]))
        elements.append(status_table)
    elements.append(Spacer(1, 15))
    
    # Theo thể loại
    elements.append(Paragraph("<b>3. SACH THEO THE LOAI</b>", styles['CustomBold']))
    by_category = stats.get('by_category', [])
    category_data = [['The loai', 'So luong']]
    for name, count in by_category:
        category_data.append([name, str(count)])
    
    if len(category_data) > 1:
        cat_table = Table(category_data, colWidths=[10*cm, 4*cm])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ]))
        elements.append(cat_table)
    elements.append(Spacer(1, 15))
    
    # Sách được mượn nhiều nhất
    elements.append(Paragraph("<b>4. SACH DUOC MUON NHIEU NHAT</b>", styles['CustomBold']))
    most_borrowed = stats.get('most_borrowed', [])
    borrowed_data = [['STT', 'Tieu de', 'Tac gia', 'Luot muon']]
    for i, (title, author, count) in enumerate(most_borrowed, 1):
        borrowed_data.append([str(i), title, author or 'N/A', str(count)])
    
    if len(borrowed_data) > 1:
        borrowed_table = Table(borrowed_data, colWidths=[1.5*cm, 8*cm, 4*cm, 2.5*cm])
        borrowed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ]))
        elements.append(borrowed_table)
    
    doc.build(elements)
    return output_path


def generate_borrow_statistics_report(stats: dict, output_path: str = None) -> str:
    """
    Tạo báo cáo thống kê mượn trả
    
    Args:
        stats: Dữ liệu thống kê
        output_path: Đường dẫn file output (tùy chọn)
    
    Returns:
        Đường dẫn file PDF đã tạo
    """
    if output_path is None:
        filename = f"thong_ke_muon_tra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = create_styles()
    elements = []
    
    # Tiêu đề
    elements.append(Paragraph("THU VIEN SO", styles['CustomTitle']))
    elements.append(Paragraph("BAO CAO THONG KE MUON TRA", styles['CustomTitle']))
    elements.append(Paragraph(f"Ngay lap: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['CustomSubtitle']))
    elements.append(Spacer(1, 20))
    
    # Tổng quan
    elements.append(Paragraph("<b>1. TONG QUAN</b>", styles['CustomBold']))
    elements.append(Paragraph(f"Tong so phieu muon: {stats.get('total_borrows', 0)}", styles['CustomNormal']))
    elements.append(Paragraph(f"So phieu qua han: {stats.get('overdue', 0)}", styles['CustomNormal']))
    elements.append(Paragraph(f"Tong tien phat: {stats.get('total_fines', 0):,.0f} VND", styles['CustomNormal']))
    elements.append(Spacer(1, 15))
    
    # Theo trạng thái
    elements.append(Paragraph("<b>2. PHIEU THEO TRANG THAI</b>", styles['CustomBold']))
    by_status = stats.get('by_status', {})
    status_data = [['Trang thai', 'So luong']]
    status_map = {'DANG_MUON': 'Dang muon', 'DA_TRA': 'Da tra', 'QUA_HAN': 'Qua han'}
    for status, count in by_status.items():
        status_data.append([status_map.get(status, status), str(count)])
    
    if len(status_data) > 1:
        status_table = Table(status_data, colWidths=[8*cm, 4*cm])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ]))
        elements.append(status_table)
    
    doc.build(elements)
    return output_path


def generate_reader_card(reader_data: dict, output_path: str = None) -> str:
    """
    Tạo thẻ đọc giả
    
    Args:
        reader_data: Thông tin đọc giả
        output_path: Đường dẫn file output (tùy chọn)
    
    Returns:
        Đường dẫn file PDF đã tạo
    """
    if output_path is None:
        filename = f"the_doc_gia_{reader_data.get('ma_doc_gia', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = create_styles()
    elements = []
    
    # Tiêu đề
    elements.append(Paragraph("THU VIEN SO", styles['CustomTitle']))
    elements.append(Paragraph("THE DOC GIA", styles['CustomTitle']))
    elements.append(Spacer(1, 30))
    
    # Thông tin thẻ
    card_info = [
        ['Ma the:', str(reader_data.get('ma_the', 'N/A'))],
        ['Ma doc gia:', reader_data.get('ma_doc_gia', 'N/A')],
        ['Ho va ten:', reader_data.get('ho_ten', 'N/A')],
        ['Dia chi:', reader_data.get('dia_chi', 'N/A')],
        ['So dien thoai:', reader_data.get('so_dt', 'N/A')],
        ['Email:', reader_data.get('email', 'N/A')],
        ['Ngay cap:', reader_data.get('ngay_cap', 'N/A')],
        ['Ngay het han:', reader_data.get('ngay_het_han', 'N/A')],
        ['Trang thai:', reader_data.get('trang_thai_the', 'N/A')],
    ]
    
    card_table = Table(card_info, colWidths=[5*cm, 10*cm])
    card_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 30))
    
    # Lưu ý
    elements.append(Paragraph("<b>LUU Y:</b>", styles['CustomBold']))
    elements.append(Paragraph("- The doc gia co gia tri trong 1 nam ke tu ngay cap.", styles['CustomNormal']))
    elements.append(Paragraph("- Vui long mang the khi den thu vien.", styles['CustomNormal']))
    elements.append(Paragraph("- Bao ngay cho thu vien khi mat the.", styles['CustomNormal']))
    
    doc.build(elements)
    return output_path
