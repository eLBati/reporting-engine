from odoo import models, fields

TEXT_ALIGNMENT_LIST = [
    ('left', 'Left'),
    ('right', 'Right'),
    ('center', 'Center'),
]

class PDFGenReportPlaceholder(models.Model):
    _name = "pdfgen.fixed.report.placeholder"
    _description = "PDF Generator Placeholder"

    name = fields.Char(
        string="Name",
        required=True
    )

    report_id = fields.Many2one(
        comodel_name="pdfgen.fixed.report",
        string="Related report"
    )

    text_field = fields.Char(
        string="Code",
        required=True
    )

    text_size = fields.Integer(
        string="Font size",
        required=True
    )

    text_color = fields.Integer(
        string="Color",
        required=True
    )

    text_font_id = fields.Many2one(
        comodel_name="pdfgen.fixed.report.placeholder.font",
        string="Font",
        required=True
    )

    text_alignment = fields.Selection(
        selection=TEXT_ALIGNMENT_LIST,
        string="Alignment",
        required=True,
        default=TEXT_ALIGNMENT_LIST[0][0]
    )

    page = fields.Integer(
        string="Page",
        required=True,
        default=1
    )

    position_x = fields.Integer(
        string="Position X",
        required=True
    )

    position_y = fields.Integer(
        string="Position Y",
        required=True
    )
