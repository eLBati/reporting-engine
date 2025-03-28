from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from logging import getLogger

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import PyPDF2
import base64

_logger = getLogger(__name__)

TEXT_COLOR_LIST = [
    [1.000, 1.000, 1.000],
    [0.592, 0.106, 0.051],
    [0.561, 0.278, 0.043],
    [0.541, 0.439, 0.024],
    [0.059, 0.369, 0.525],
    [0.404, 0.227, 0.325],
    [0.478, 0.075, 0.078],
    [0.141, 0.412, 0.475],
    [0.224, 0.267, 0.373],
    [0.671, 0.063, 0.294],
    [0.145, 0.612, 0.404],
    [0.380, 0.231, 0.498],
]

class PDFGenReportTemplate(models.Model):
    _name = "pdfgen.fixed.report.template"
    _description = "Report Generator Template"

    name = fields.Char(
        string="Name",
        required=True
    )

    code = fields.Char(
        string="Identified by",
        required=True
    )

    template_pdf = fields.Binary(
        string="Template",
        required=False
    )

    file_name = fields.Char(
        string="File Name",
        required=False
    )

    placeholder_ids = fields.One2many(
        comodel_name="pdfgen.fixed.report.placeholder",
        inverse_name="report_id",
        string="Fields",
        required=True
    )


class PDFGenReport(models.Model):
    _name = "pdfgen.fixed.report"
    _description = "Fixed Report"

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report", required=True
    )

    @api.model
    def create(self, values):
        res = super(PDFGenReport, self).create(values)
        res._validate_template_extension(values.get('file_name'))

        return res

    def write(self, values):
        res = super(PDFGenReport, self).write(values)

        for record in self:
            record._validate_template_extension(record.file_name)

        return res

    def _validate_template_extension(self, filename):
        if filename and filename.split('.')[-1].lower() != 'pdf':
            raise ValidationError(_("Only PDF extensions allowed"))

    @api.model
    def get_report(self, code):
        return self.env['pdfgen.fixed.report'].search([('code', '=', code)], limit=1)

    def generate_report(self, res_id, data=None):
        try:
            template = io.BytesIO(base64.b64decode(
                self.ir_actions_report_id.pdfgen_fixed_report_template_id.template_pdf
            ))
            existing_pdf = PyPDF2.PdfFileReader(template)
            pdf_writer = PyPDF2.PdfFileWriter()
        except:
            raise ValidationError(_('Could not load provided template, maybe is broken'))

        try:
            record = self.env[self.ir_actions_report_id.model].browse(res_id)
        except:
            raise ValidationError(_("Could not generate report, record not found: %d" % (res_id)))

        try:
            for page in range(existing_pdf.numPages):
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)

                placeholders = self.env['pdfgen.fixed.report.placeholder'].search([('id','in',self.ir_actions_report_id.pdfgen_fixed_report_template_id.placeholder_ids.ids), ('page','=',page+1)])

                for placeholder in placeholders:

                    rgb = TEXT_COLOR_LIST[int(placeholder.text_color)]
                    placeholder.text_font_id.register_font()
                    can.setFont(placeholder.text_font_id.name, placeholder.text_size)
                    can.setFillColorRGB(*rgb)

                    try:
                        placeholder_value = eval(placeholder.text_field)
                    except Exception as ex:
                        raise ValidationError(_(
                            "An error has occurred while processing %s (ID: %i)'s field on report %s.\n\r%s" % (placeholder.name, placeholder.id, self.name, str(ex))
                        ))

                    if placeholder_value:
                        if placeholder.text_alignment == 'left':
                            can.drawString(placeholder.position_x, placeholder.position_y, str(placeholder_value))
                        elif placeholder.text_alignment == 'right':
                            can.drawRightString(placeholder.position_x, placeholder.position_y, str(placeholder_value))
                        elif placeholder.text_alignment == 'center':
                            can.drawCentredString(placeholder.position_x, placeholder.position_y, str(placeholder_value))

                can.save()
                packet.seek(0)

                new_pdf = PyPDF2.PdfFileReader(packet)
                new_page = existing_pdf.getPage(page)

                if placeholders:
                    new_page.mergePage(new_pdf.getPage(0))

                pdf_writer.addPage(new_page)

            output = io.BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            return base64.b64encode(output.read()).decode(), "pdf"
        except Exception as ex:
            _logger.info("Failed elaborating resource %d >> %s" % (res_id, ex))
            raise ValidationError("An error has occurred: %s" % (str(ex)))

    def preview_report(self):
        return {
            'name': _("Preview"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pdfgen.preview.wizard',
            'target': 'new',
            'context': {
                'default_report_id': self.id
            },
            'flags': {'initial_mode': 'view'}
        }

    def action_list_action_server(self):
        return {
            'name': _('%s Actions') % (self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.actions.server',
            'target': 'current',
            'domain': [('pdfgen_fixed_report_id', '=', self.id)],
            'context': self._default_action_server_values()
        }

    def action_add_action_server(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.actions.server',
            'target': 'new',
            'context': self._default_action_server_values()
        }

    def _compute_ir_action_server_count(self):
        for record in self:
            record.ir_action_server_count = self.env['ir.actions.server'].sudo().search([('pdfgen_fixed_report_id', '=', record.id)], count=True)