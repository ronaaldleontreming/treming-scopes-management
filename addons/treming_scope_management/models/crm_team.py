from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):
    _inherit = "crm.team"
    
    trscma_include_technical_proposal_tr = fields.Boolean(
        string="Include Technical Proposal",
        help=_("If enabled, a unified PDF (company info + service info + scope + quotation) " "will be generated and used for emails. ")
    )
    
    trscma_proposal_header_pdf_tr = fields.Binary(
        string="Header",
        attachment=True
    )
    trscma_proposal_header_pdf_filename_tr = fields.Char(string="Header filename")
    
    trscma_proposal_footer_pdf_tr = fields.Binary(
        string="Footer",
        attachment=True
    )
    trscma_proposal_footer_pdf_filename_tr = fields.Char(string="Footer filename")
    
    
    @api.constrains("trscma_include_technical_proposal_tr")
    def _check_min_pdfs(self):
        for team in self:
            if not team.trscma_include_technical_proposal_tr:
                continue
            if not team.trscma_proposal_header_pdf_tr:
                raise ValidationError(_("Debe adjuntar el Header"))
            if not team.trscma_proposal_footer_pdf_tr:
                raise ValidationError(_("Debe adjuntar el Footer"))