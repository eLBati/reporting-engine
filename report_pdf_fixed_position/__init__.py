from . import models, wizards
from odoo.api import Environment, SUPERUSER_ID
from reportlab.pdfgen import canvas
import io

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    fonts = canvas.Canvas(io.BytesIO()).getAvailableFonts()

    for font in fonts:
        try:
            env['pdfgen.fixed.report.placeholder.font'].sudo().create({"name": font, "default_font": True})
        except:
            pass
    
    env.cr.commit()