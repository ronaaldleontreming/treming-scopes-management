from odoo import models, fields, api
import base64
from odoo.exceptions import UserError


# Optional: Import pypdf for adding form fields (for inputs/labels in Quote Builder)
# from pypdf import PdfWriter, PdfReader
# import io

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_include_technical_proposal = fields.Boolean(
        related='team_id.trscma_include_technical_proposal_tr',
        string="Team Includes Technical Proposal",
        readonly=True
    )

    related_scope_ids = fields.Many2many(
        'scope.management',
        string="Detected Scopes",
        help="Scopes automatically detected from products in the quotation.",
        compute="_compute_related_scope_ids",
        store=False
    )

    has_related_scopes = fields.Boolean(
        string="Has Related Scopes",
        compute="_compute_has_related_scopes",
        store=True
    )

    related_scope_products = fields.Char(
        string="Products with Scopes",
        compute="_compute_related_scope_products",
        store=True
    )

    scope_ids = fields.One2many("scope.management", "sale_order_id", string="Scopes")

    show_related_scope_products = fields.Boolean(
        string="Show Related Scope Products",
        compute="_compute_show_related_scope_products",
        store=True
    )

    technical_proposal_document_id = fields.Many2one(
        'ir.attachment',  # Ajustado para el modelo personalizado quotation.document
        string="Technical Proposal Document",
        help="Documento PDF generado desde los scopes para adjuntar en Quote Builder."
    )

    @api.depends('related_scope_ids.product_id')
    def _compute_related_scope_products(self):
        for order in self:
            product_names = order.related_scope_ids.mapped('product_id.name')
            order.related_scope_products = ", ".join(product_names) if product_names else "No products"

    @api.depends('order_line.product_id')
    def _compute_related_scope_ids(self):
        for order in self:
            product_ids = order.order_line.mapped('product_id').ids
            scopes = self.env['scope.management'].search([('product_id', 'in', product_ids)])
            order.related_scope_ids = scopes

    @api.depends('related_scope_ids')
    def _compute_has_related_scopes(self):
        for order in self:
            order.has_related_scopes = bool(order.related_scope_ids)

    @api.depends('team_id', 'related_scope_ids.sales_team', 'team_include_technical_proposal')
    def _compute_show_related_scope_products(self):
        for order in self:
            team_matches = any(scope.sales_team == order.team_id for scope in order.related_scope_ids)
            order.show_related_scope_products = team_matches and order.team_include_technical_proposal

    def action_attach_technical_proposal(self):
        """Generate the PDF from scopes and attach it to the Quotation Builder."""
        self.ensure_one()
        if not self.related_scope_ids:
            raise UserError("No related scopes to generate the PDF.")

        # Get the report
        try:
            report = self.env.ref('treming_scope_management.action_report_scope_proposal')
            _logger.info(f"Using report: treming_scope_management.action_report_scope_proposal for order {self.name}")
        except ValueError as e:
            _logger.error(f"Report 'treming_scope_management.action_report_scope_proposal' not found: {str(e)}")
            raise UserError("The report 'treming_scope_management.action_report_scope_proposal' is not defined or not found.")

        # Generate the scope PDF
        try:
            pdf_content, _ = report._render_qweb_pdf(report_ref=report, res_ids=[self.id])
        except Exception as e:
            _logger.error(f"Failed to render PDF for order {self.name}: {str(e)}")
            raise UserError(f"Failed to generate PDF for order {self.name}: {str(e)}")

        # Merge with header and footer if defined
        pdf_streams = []
        if self.team_id.trscma_proposal_header_pdf_tr:
            pdf_streams.append(base64.b64decode(self.team_id.trscma_proposal_header_pdf_tr))
        pdf_streams.append(pdf_content)
        if self.team_id.trscma_proposal_footer_pdf_tr:
            pdf_streams.append(base64.b64decode(self.team_id.trscma_proposal_footer_pdf_tr))

        try:
            merged_pdf = pdf.merge_pdf(pdf_streams)
            datas = base64.b64encode(merged_pdf)
        except Exception as e:
            _logger.error(f"Failed to merge PDFs for order {self.name}: {str(e)}")
            raise UserError(f"Failed to merge PDFs for order {self.name}: {str(e)}")

        # Update or create the attachment
        if self.technical_proposal_document_id:
            self.technical_proposal_document_id.write({
                'datas': datas,
                'mimetype': 'application/pdf',
                'name': f'Technical Proposal for {self.name}.pdf',
            })
        else:
            doc = self.env['ir.attachment'].create({
                'name': f'Technical Proposal for {self.name}.pdf',
                'type': 'binary',
                'datas': datas,
                'mimetype': 'application/pdf',
                'res_model': 'sale.order',
                'res_id': self.id,
            })
            self.technical_proposal_document_id = doc

        # Return action to open the Quotation Builder tab
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'view_id': self.env.ref('sale_quotation_builder.sale_order_form_quote_builder').id,
        }

    def action_print_technical_proposal(self):
        """Attach the PDF and print it."""
        self.ensure_one()
        _logger.info(f"Attempting to print technical proposal for order {self.name}")
        self.action_attach_technical_proposal()
        try:
            report = self.env.ref('treming_scope_management.action_report_scope_proposal')
            _logger.info(f"Rendering report: treming_scope_management.action_report_scope_proposal for order {self.name}")
        except ValueError as e:
            _logger.error(f"Report 'treming_scope_management.action_report_scope_proposal' not found: {str(e)}")
            raise UserError("The report 'treming_scope_management.action_report_scope_proposal' is not defined or not found.")
        return report.report_action(self)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_scope(self):
        if self.order_id:
            self.order_id._compute_related_scope_ids()
