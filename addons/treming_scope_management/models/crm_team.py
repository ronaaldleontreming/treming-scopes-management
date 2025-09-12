from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    trscma_include_technical_proposal_tr = fields.Boolean(
        string="Include Technical Proposal",
        help=_(
            "If enabled, a unified PDF (company info + service info + scope + quotation) will be generated and used for emails.")
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

    # Campos para manejar los attachments
    header_attachment_id = fields.Many2one('ir.attachment', string="Header Attachment")
    footer_attachment_id = fields.Many2one('ir.attachment', string="Footer Attachment")

    @api.constrains("trscma_include_technical_proposal_tr")
    def _check_min_pdfs(self):
        for team in self:
            if not team.trscma_include_technical_proposal_tr:
                continue
            if not team.trscma_proposal_header_pdf_tr:
                raise ValidationError(_("Debe adjuntar el Header"))
            if not team.trscma_proposal_footer_pdf_tr:
                raise ValidationError(_("Debe adjuntar el Footer"))

    @api.model
    def create(self, vals):
        record = super(CrmTeam, self).create(vals)
        record._manage_attachments()
        return record

    def write(self, vals):
        result = super(CrmTeam, self).write(vals)
        self._manage_attachments()
        return result

    def _manage_attachments(self):
        for team in self:
            # Manejar header
            if team.trscma_proposal_header_pdf_tr:
                attachment_vals = {
                    'name': team.trscma_proposal_header_pdf_filename_tr or 'header.pdf',
                    'datas': team.trscma_proposal_header_pdf_tr,
                    'res_model': 'crm.team',
                    'res_id': team.id,
                    'type': 'binary',
                }
                if team.header_attachment_id:
                    team.header_attachment_id.write(attachment_vals)
                else:
                    attachment = self.env['ir.attachment'].create(attachment_vals)
                    team.header_attachment_id = attachment.id

            # Manejar footer
            if team.trscma_proposal_footer_pdf_tr:
                attachment_vals = {
                    'name': team.trscma_proposal_footer_pdf_filename_tr or 'footer.pdf',
                    'datas': team.trscma_proposal_footer_pdf_tr,
                    'res_model': 'crm.team',
                    'res_id': team.id,
                    'type': 'binary',
                }
                if team.footer_attachment_id:
                    team.footer_attachment_id.write(attachment_vals)
                else:
                    attachment = self.env['ir.attachment'].create(attachment_vals)
                    team.footer_attachment_id = attachment.id