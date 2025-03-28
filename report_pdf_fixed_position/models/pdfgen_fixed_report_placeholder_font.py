from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from logging import getLogger
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import base64

_logger = getLogger(__name__)

class PDFGenReportPlaceholderFont(models.Model):
    _name = "pdfgen.fixed.report.placeholder.font"
    _description = "PDF Generator Placeholder font"
    
    name = fields.Char(
        string="Name",
        required=True
    )

    font = fields.Binary(
        string="Font",
        required=False
    )
    
    default_font = fields.Boolean(
        string="Default Font",
        default=False
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Font already registered with this name'),
    ]

    def register_font(self):
        for record in self:
            try:
                if record.font:
                    font = io.BytesIO(base64.b64decode(record.font))
                    pdfmetrics.registerFont(TTFont(record.name, font))

                canvas.Canvas(io.BytesIO()).setFont(record.name, 12)
            except:
                raise ValidationError(_("Could not load font %s, ensure TTF file is valid") % (record.name))
    
    @api.model
    def create(self, values):
        res = super(PDFGenReportPlaceholderFont, self).create(values)
        res.register_font()

        return res
        
    def write(self, values):
        res = super(PDFGenReportPlaceholderFont, self).create(values)

        for record in res:
            record.register_font()

        return res
