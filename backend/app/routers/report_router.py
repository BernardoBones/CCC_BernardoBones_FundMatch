from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/report", tags=["report"])


def draw_title(pdf, text, y):
    pdf.setFillColor(colors.HexColor("#2E3A59"))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(2 * cm, y, text)
    pdf.setFillColor(colors.black)
    return y - 1.3 * cm


def draw_section_header(pdf, text, y):
    pdf.setFillColor(colors.HexColor("#4A6FA5"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(2 * cm, y, text)
    pdf.setFillColor(colors.black)

    # linha sutil
    y -= 0.3 * cm
    pdf.setStrokeColor(colors.HexColor("#4A6FA5"))
    pdf.setLineWidth(1)
    pdf.line(2 * cm, y, 19 * cm, y)

    return y - 0.8 * cm


def ensure_space(pdf, y, height, margin=2*cm):
    """Evita escrever fora da página."""
    if y < margin + height:
        pdf.showPage()
        return A4[1] - 2 * cm
    return y


@router.get("/generate", summary="Gera relatório PDF do usuário atual")
def generate_report(db: Session = Depends(get_db),
                    user=Depends(get_current_user_from_token)):

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ====== INÍCIO DO PDF ======
    y = height - 2 * cm
    pdf.setTitle("Relatório FundMatch")

    # Título grande
    y = draw_title(pdf, "Relatório FundMatch", y)

    # Info do usuário
    pdf.setFont("Helvetica", 12)
    pdf.drawString(2 * cm, y, f"Usuário: {user.name}  |  Email: {user.email}")
    y -= 1 * cm

    # ===== Favoritos =====
    favorites = crud.list_favorites(db, user.id)
    y = draw_section_header(pdf, "⭐ Fundos Favoritados", y)

    pdf.setFont("Helvetica", 11)
    if favorites:
        for f in favorites:
            y = ensure_space(pdf, y, 1*cm)

            pdf.drawString(2.3 * cm, y, f"• {f.name} ({f.cnpj})")
            y -= 0.5 * cm

            pdf.setFillColor(colors.HexColor("#666666"))
            pdf.drawString(2.8 * cm, y, f"Classe: {f.class_name}")
            pdf.setFillColor(colors.black)

            y -= 0.7 * cm
    else:
        pdf.drawString(2.3 * cm, y, "Nenhum fundo favoritado.")
        y -= 1 * cm

    # ===== Recomendações =====
    recs = crud.get_recommendations(db, user.id)
    y = draw_section_header(pdf, "💡 Fundos Recomendados", y)

    pdf.setFont("Helvetica", 11)
    if recs:
        for f in recs:
            y = ensure_space(pdf, y, 1*cm)

            pdf.drawString(2.3 * cm, y, f"• {f.name} ({f.cnpj})")
            y -= 0.5 * cm

            pdf.setFillColor(colors.HexColor("#666666"))
            pdf.drawString(2.8 * cm, y, f"Rentabilidade: {f.rentability or 0:.2f}%")
            pdf.setFillColor(colors.black)

            y -= 0.7 * cm
    else:
        pdf.drawString(2.3 * cm, y, "Nenhuma recomendação disponível.")
        y -= 1 * cm

    # ===== Rodapé =====
    y = ensure_space(pdf, y, 2 * cm)
    pdf.setStrokeColor(colors.lightgrey)
    pdf.line(2 * cm, 2 * cm, 19 * cm, 2 * cm)

    pdf.setFillColor(colors.HexColor("#777777"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(2 * cm, 1.5 * cm, "Relatório gerado automaticamente pelo sistema FundMatch")
    pdf.setFillColor(colors.black)

    # Finaliza
    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=relatorio_{user.name}.pdf"
        },
    )
