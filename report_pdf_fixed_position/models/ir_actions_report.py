from odoo import models, fields, api


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("pdfgen_fixed_report", "PDF Fixed position")],
        ondelete={
            "pdfgen_fixed_report": "cascade",
        },
    )
    pdfgen_fixed_report_template_id = fields.Many2one("pdfgen.fixed.report.template", "Template")

    @api.model
    def _render_pdfgen_fixed_report(self, report_ref, res_ids, data=None):
        report = self._get_report(report_ref)
        if report.report_type != "pdfgen_fixed_report":
            raise RuntimeError(
                "pdfgen_fixed_report rendition is only available on pdfgen_fixed_report report.\n"
                "(current: '{}', expected 'pdfgen_fixed_report'".format(report.report_type)
            )
        return (
            self.env["pdfgen.fixed.report"]
            .create({"ir_actions_report_id": report.id})
            .generate_report(res_ids, data)
        )