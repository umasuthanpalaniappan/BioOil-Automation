import io
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.drift import check_drift
from app.model_registry import registry
from app.physics_validation import validate_feedstock, validate_prediction
from app.schemas import PredictionRequest

router = APIRouter(tags=["export"])


@router.post("/export/pdf")
def export_pdf(req: PredictionRequest):
    if not registry.loaded:
        raise HTTPException(503, "Models not loaded on server")

    feature_dict = req.feedstock.model_dump(by_alias=True)
    pred, ci, used = registry.predict_oc(feature_dict, req.model_name or "best")
    physics_flags = validate_feedstock(req.feedstock) + validate_prediction(pred, "O/C")
    drift_flags = check_drift(feature_dict)
    secondary = registry.predict_secondary(feature_dict)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Bio-Oil Pyrolysis Prediction Report", styles["Title"]),
        Paragraph(f"Generated: {datetime.utcnow().isoformat()}Z", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"Model used: {used}", styles["Heading2"]),
        Paragraph(f"Predicted O/C: {pred:.4f}"
                  + (f"  (95% CI: {ci[0]:.4f} - {ci[1]:.4f})" if ci else ""), styles["Normal"]),
        Spacer(1, 12),
    ]

    if secondary:
        story.append(Paragraph("Secondary predictions", styles["Heading3"]))
        for k, v in secondary.items():
            story.append(Paragraph(f"{k}: {v:.3f}", styles["Normal"]))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Feedstock inputs", styles["Heading3"]))
    table_data = [["Field", "Value"]] + [[k, str(v)] for k, v in feature_dict.items()]
    t = Table(table_data)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, "grey"),
                            ("BACKGROUND", (0, 0), (-1, 0), "#dddddd")]))
    story.append(t)
    story.append(Spacer(1, 12))

    if physics_flags:
        story.append(Paragraph("Physics validation flags", styles["Heading3"]))
        for f in physics_flags:
            story.append(Paragraph(f"[{f.severity}] {f.field}: {f.message}", styles["Normal"]))
        story.append(Spacer(1, 12))

    if drift_flags:
        story.append(Paragraph("Data drift flags", styles["Heading3"]))
        for f in drift_flags:
            story.append(Paragraph(f.message, styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=prediction_report.pdf"},
    )
