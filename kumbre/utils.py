from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.http import HttpResponse
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from decimal import Decimal

def generar_factura_pdf(compra, productos_compra, reservas_compra, total_productos, total_reservas, total_a_pagar):
    """
    Genera un PDF de factura con diseño compacto basado en los detalles de la compra.
    Versión optimizada para ocupar menos espacio.
    """
    # Importaciones básicas para ReportLab
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    # Crear un buffer para guardar el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF con ReportLab (márgenes más pequeños)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos para el documento
    styles = getSampleStyleSheet()
    
    # Estilos personalizados más compactos
    centrado = ParagraphStyle(
        name='Centrado',
        parent=styles['Normal'],
        alignment=1,  # Centro = 1
        fontSize=9,
        spaceAfter=3
    )
    
    normal_small = ParagraphStyle(
        name='NormalSmall',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=2
    )
    
    titulo_seccion = ParagraphStyle(
        name='TituloSeccion',
        parent=styles['Normal'],
        alignment=1,
        fontSize=10,
        textColor=colors.HexColor("#2C5545"),
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    
    # Encabezado más compacto
    elements.append(Paragraph(f"<font color='#2C5545' size='13'><b>FACTURA LA KUMBRE</b></font>", centrado))
    elements.append(Paragraph(f"<font color='#2C5545' size='9'><b>Gracias por confiar en nosotros</b></font>", centrado))
    elements.append(Spacer(1, 0.15*inch))
    
    # Mensaje personalizado más corto
    elements.append(Paragraph(f"<font color='#2C5545' size='9'><b>Hola, {compra.nombre}</b></font>", normal_small))
    elements.append(Paragraph("Gracias por elegir La Kumbre Ecohotel. Presenta esta factura al llegar para validar tu reserva.", normal_small))
    elements.append(Spacer(1, 0.15*inch))
    
    # --- INFORMACIÓN DEL CLIENTE ---
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", titulo_seccion))
    
    # Datos del cliente en una sola línea cuando sea posible
    elements.append(Paragraph(f"<b>Cliente:</b> {compra.nombre} | <b>Email:</b> {compra.email}", normal_small))
    elements.append(Paragraph(f"<b>Teléfono:</b> {compra.telefono}", normal_small))
    
    # Método de pago
    METHOD_NAMES = {
        'nequi': 'Nequi',
        'daviplata': 'Daviplata',
        'bancolombia': 'Bancolombia',
        'efectivo': 'Efectivo',
        'tarjeta': 'Tarjeta de Crédito/Débito'
    }
    nombre_metodo = METHOD_NAMES.get(compra.metodo_pago, 'Desconocido')
    elements.append(Paragraph(f"<b>Método de pago:</b> {nombre_metodo}", normal_small))
    elements.append(Spacer(1, 0.15*inch))
    
    # --- PRODUCTOS ---
    if productos_compra:
        # Separar comidas y bebidas
        comidas = [p for p in productos_compra if p.get('tipo_producto') == 'comida']
        bebidas = [p for p in productos_compra if p.get('tipo_producto') == 'bebida']
        otros = [p for p in productos_compra if p.get('tipo_producto') not in ['comida', 'bebida']]
        
        # COMIDAS
        if comidas:
            elements.append(Paragraph("🍽️ COMIDAS", titulo_seccion))
            
            data_comidas = [['Producto', 'Cant.', 'P. Unit.', 'Total']]
            subtotal_comidas = 0
            for producto in comidas:
                nombre_completo = producto['nombre']
                if producto.get('presentacion'):
                    nombre_completo += f" ({producto['presentacion']})"
                    
                data_comidas.append([
                    nombre_completo,
                    str(producto['cantidad']),
                    f"${producto['precio_unitario']:,.0f}",
                    f"${producto['precio_total']:,.0f}"
                ])
                subtotal_comidas += producto['precio_total']
            
            # Agregar subtotal de comidas
            data_comidas.append(['', '', 'Subtotal:', f"${subtotal_comidas:,.0f}"])
            
            tabla_comidas = Table(data_comidas, colWidths=[3.2*inch, 0.6*inch, 0.9*inch, 0.9*inch])
            tabla_comidas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D4691D")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#FFF3E0")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabla_comidas)
            elements.append(Spacer(1, 0.1*inch))
        
        # BEBIDAS
        if bebidas:
            elements.append(Paragraph("🍹 BEBIDAS", titulo_seccion))
            
            data_bebidas = [['Producto', 'Present.', 'Cant.', 'P. Unit.', 'Total']]
            subtotal_bebidas = 0
            for producto in bebidas:
                data_bebidas.append([
                    producto['nombre'],
                    producto.get('presentacion', 'N/A'),
                    str(producto['cantidad']),
                    f"${producto['precio_unitario']:,.0f}",
                    f"${producto['precio_total']:,.0f}"
                ])
                subtotal_bebidas += producto['precio_total']
            
            # Agregar subtotal de bebidas
            data_bebidas.append(['', '', '', 'Subtotal:', f"${subtotal_bebidas:,.0f}"])
            
            tabla_bebidas = Table(data_bebidas, colWidths=[2.2*inch, 0.8*inch, 0.5*inch, 0.8*inch, 0.9*inch])
            tabla_bebidas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E90FF")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E3F2FD")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabla_bebidas)
            elements.append(Spacer(1, 0.1*inch))
        
        # OTROS PRODUCTOS (si los hay)
        if otros:
            elements.append(Paragraph("📦 OTROS PRODUCTOS", titulo_seccion))
            
            data_otros = [['Producto', 'Cant.', 'P. Unit.', 'Total']]
            for producto in otros:
                data_otros.append([
                    producto['nombre'],
                    str(producto['cantidad']),
                    f"${producto['precio_unitario']:,.0f}",
                    f"${producto['precio_total']:,.0f}"
                ])
            
            tabla_otros = Table(data_otros, colWidths=[3.2*inch, 0.6*inch, 0.9*inch, 0.9*inch])
            tabla_otros.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6C757D")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ]))
            elements.append(tabla_otros)
            elements.append(Spacer(1, 0.1*inch))
        
        # Información de horario y fecha en una línea
        info_adicional = []
        if compra.horario_comida:
            info_adicional.append(f"<b>Hora:</b> {compra.horario_comida.strftime('%I:%M %p')}")
        if compra.fecha_entrega:
            info_adicional.append(f"<b>Fecha:</b> {compra.fecha_entrega.strftime('%d/%m/%Y')}")
        
        if info_adicional:
            elements.append(Paragraph(" | ".join(info_adicional), normal_small))
    
    # --- RESERVAS ---
    if reservas_compra:
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph("DETALLE DE RESERVAS", titulo_seccion))
        
        # Crear tabla de reservas más compacta
        data_reservas = [['Cabaña', 'Fecha', 'Pers.', 'Adic.', 'Total']]
        for reserva in reservas_compra:
            data_reservas.append([
                reserva['cabana'],
                reserva['fecha'].strftime('%d/%m/%Y'),
                str(reserva['personas']),
                str(reserva['personas_adicionales']),
                f"${reserva['precio']:,.0f}"
            ])
        
        # Añadir total de reservas
        data_reservas.append(['', '', '', 'Total:', f"${total_reservas:,.0f}"])
        
        # Crear la tabla con estilo compacto
        reservas_tabla = Table(data_reservas, colWidths=[2.2*inch, 1*inch, 0.6*inch, 0.6*inch, 1*inch])
        reservas_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C5545")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(reservas_tabla)
    
    # --- RESUMEN DE PAGOS ---
    elements.append(Spacer(1, 0.2*inch))
    
    # Calcular totales
    total_general = total_productos + total_reservas
    saldo_pendiente = Decimal(str(total_general)) - Decimal(str(total_a_pagar))
    
    # Tabla de resumen de pagos más compacta
    elements.append(Paragraph("RESUMEN DE PAGOS", titulo_seccion))
    
    data_resumen = [
        ['Total General:', f"${total_general:,.0f}"],
        ['Anticipo Pagado:', f"${total_a_pagar:,.0f}"],
        ['Saldo Pendiente:', f"${saldo_pendiente:,.0f}"]
    ]
    
    resumen_tabla = Table(data_resumen, colWidths=[3.5*inch, 2*inch])
    resumen_tabla.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E8F5E8")),  # Total General
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#E8F5E8")),  # Anticipo
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#FFE8E8")),  # Saldo Pendiente
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(resumen_tabla)
    
    # Mensaje informativo sobre el saldo más compacto
    elements.append(Spacer(1, 0.15*inch))
    if saldo_pendiente > 0:
        if reservas_compra:
            mensaje_saldo = "El saldo restante debe cancelarse al llegar a La Kumbre."
        else:
            mensaje_saldo = "El saldo restante debe cancelarse al llegar a La Kumbre."
        
        elements.append(Paragraph(f"<font color='#D32F2F' size='8'><b>IMPORTANTE:</b> {mensaje_saldo}</font>", normal_small))
    else:
        elements.append(Paragraph(f"<font color='#388E3C' size='9'><b>✓ PAGO COMPLETO REALIZADO</b></font>", centrado))
    
    # --- PIE DE PÁGINA ---
    elements.append(Spacer(1, 0.3*inch))
    pie_style = ParagraphStyle(
        name='Pie',
        parent=styles['Normal'],
        alignment=1,
        fontSize=8,
        spaceAfter=1
    )
    
    elements.append(Paragraph("Gracias por tu compra. ¡Esperamos verte pronto en La Kumbre!", pie_style))
    elements.append(Paragraph("<b>Tel:</b> +57 310 883 1683 | <b>Email:</b> lakumbredelhuila01@gmail.com", pie_style))
    elements.append(Paragraph("Garzón- Huila, Vereda Alto San Isidro", pie_style))
    
    # Construir el PDF y cerrar el archivo
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def generar_factura_response(compra, productos_compra, reservas_compra, total_productos, total_reservas, total_a_pagar):
    """
    Genera un HttpResponse con el PDF de la factura para descargar.
    Versión compacta optimizada.
    """
    pdf = generar_factura_pdf(compra, productos_compra, reservas_compra, total_productos, total_reservas, total_a_pagar)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_La_Kumbre.pdf"; filename*=UTF-8\'\'factura_La_Kumbre.pdf'
    response.write(pdf)
    return response