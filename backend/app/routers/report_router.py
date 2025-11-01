from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/report", tags=["report"])


from fastapi.responses import StreamingResponse

@router.get("/generate", summary="Gera relatório PDF do usuário atual")
def generate_report(db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    """Gera um relatório PDF com fundos, favoritos e recomendações do usuário."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 2 * cm
    pdf.setTitle("Relatório FundMatch")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(2 * cm, y, "Relatório FundMatch")
    y -= 1.2 * cm
    pdf.setFont("Helvetica", 12)
    pdf.drawString(2 * cm, y, f"Usuário: {user.name} ({user.email})")
    y -= 1 * cm

    # --- Favoritos ---
    favorites = crud.list_favorites(db, user.id)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2 * cm, y, "⭐ Fundos Favoritados")
    y -= 0.8 * cm
    pdf.setFont("Helvetica", 11)
    if favorites:
        for f in favorites:
            pdf.drawString(2 * cm, y, f"- {f.name} ({f.cnpj}) | Classe: {f.class_name}")
            y -= 0.6 * cm
            if y < 2 * cm:
                pdf.showPage()
                y = height - 2 * cm
    else:
        pdf.drawString(2 * cm, y, "Nenhum fundo favoritado.")
        y -= 1 * cm

    # --- Recomendações ---
    recs = crud.get_recommendations(db, user.id)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2 * cm, y, "💡 Fundos Recomendados")
    y -= 0.8 * cm
    pdf.setFont("Helvetica", 11)
    if recs:
        for f in recs:
            pdf.drawString(2 * cm, y, f"- {f.name} ({f.cnpj}) | Rentabilidade: {f.rentability or 0:.2f}%")
            y -= 0.6 * cm
            if y < 2 * cm:
                pdf.showPage()
                y = height - 2 * cm
    else:
        pdf.drawString(2 * cm, y, "Nenhuma recomendação disponível.")
        y -= 1 * cm

    # Finaliza o PDF corretamente
    pdf.save()
    buffer.seek(0)

    # Usa StreamingResponse (mais seguro)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=relatorio_{user.name}.pdf"
        },
    )
