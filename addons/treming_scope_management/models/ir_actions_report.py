from odoo import models, _
import io, base64, logging, re
from odoo.tools import pdf
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
_PDF_EXT_RE = re.compile(r'\.pdf$', re.I)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def render_qweb_pdf(self, res_ids=None, data=None):
        # Primero, renderizamos el PDF normal
        result = super(IrActionsReport, self).render_qweb_pdf(res_ids, data)

        # Verificamos si es el reporte de cotización
        if self.report_name != 'sale.report_saleorder':
            return result

        # Obtenemos las órdenes de venta
        orders = self.env['sale.order'].sudo().browse(res_ids or [])

        for order in orders:
            if not order.exists():
                _logger.warning("Order %s does not exist, skipping", order.name)
                continue

            # Verificamos si debemos incluir la propuesta técnica
            team_include = getattr(order, 'team_include_technical_proposal', False)
            if not team_include:
                _logger.debug("Order %s: Skipping due to team_include_technical_proposal=False", order.name)
                continue

            try:
                streams = []

                # 1) Header PDF del equipo de ventas
                if order.team_id and order.team_id.trscma_proposal_header_pdf_tr:
                    try:
                        header_data = base64.b64decode(order.team_id.trscma_proposal_header_pdf_tr)
                        if header_data:
                            streams.append(header_data)
                            _logger.debug("Order %s: Added header PDF", order.name)
                    except Exception as e:
                        _logger.error("Order %s: Failed to decode header PDF: %s", order.name, e)

                # 2) PDF base de la cotización (el que ya renderizamos)
                if result[0]:
                    streams.append(result[0])
                    _logger.debug("Order %s: Added base quotation PDF", order.name)

                # 3) Scope PDFs
                if hasattr(order, 'related_scope_ids') and order.related_scope_ids:
                    try:
                        scope_report = self.env.ref('treming_scope_management.action_report_scope_proposal').sudo()
                        scope_pdf, _ = scope_report.render_qweb_pdf(res_ids=order.related_scope_ids.ids)
                        if scope_pdf:
                            streams.append(scope_pdf)
                            _logger.debug("Order %s: Added scope PDF", order.name)
                    except Exception as e:
                        _logger.error("Order %s: Failed to generate scope PDF: %s", order.name, e)

                # 4) PDFs adicionales del equipo de ventas
                if order.team_id:
                    domain = [
                        ('res_model', '=', 'crm.team'),
                        ('res_id', '=', order.team_id.id),
                        ('res_field', 'not in', ['trscma_proposal_header_pdf_tr', 'trscma_proposal_footer_pdf_tr']),
                        ('mimetype', 'ilike', 'pdf'),
                    ]
                    team_atts = self.env['ir.attachment'].sudo().search(domain, order='id')
                    for att in team_atts:
                        if att.datas:
                            try:
                                pdf_data = base64.b64decode(att.datas)
                                if pdf_data:
                                    streams.append(pdf_data)
                            except Exception as e:
                                _logger.error("Order %s: Failed to decode team PDF %s: %s", order.name, att.name, e)

                # 5) PDFs de productos
                for line in order.order_line:
                    product_tmpl = line.product_id.product_tmpl_id
                    if product_tmpl:
                        product_domain = [
                            ('res_model', '=', 'product.template'),
                            ('res_id', '=', product_tmpl.id),
                            ('mimetype', 'ilike', 'pdf'),
                        ]
                        product_atts = self.env['ir.attachment'].sudo().search(product_domain, order='id')
                        for att in product_atts:
                            mt = (att.mimetype or '').lower()
                            if (mt == 'application/pdf') or ('pdf' in mt) or _PDF_EXT_RE.search(att.name or ''):
                                if att.datas:
                                    streams.append(base64.b64decode(att.datas))

                # 6) Footer PDF del equipo de ventas
                if order.team_id and order.team_id.trscma_proposal_footer_pdf_tr:
                    try:
                        footer_data = base64.b64decode(order.team_id.trscma_proposal_footer_pdf_tr)
                        if footer_data:
                            streams.append(footer_data)
                            _logger.debug("Order %s: Added footer PDF", order.name)
                    except Exception as e:
                        _logger.error("Order %s: Failed to decode footer PDF: %s", order.name, e)

                # Merge de todos los PDFs
                if streams:
                    try:
                        merged = pdf.merge_pdf(streams)
                        result = (merged, 'pdf')
                        _logger.debug("Order %s: Successfully merged %d PDFs", order.name, len(streams))
                    except Exception as e:
                        _logger.error("Order %s: PDF merge failed: %s", order.name, e)
                        raise UserError(_("Failed to merge PDFs for %s: %s") % (order.display_name, e))
                else:
                    _logger.warning("Order %s: No PDFs to merge", order.name)

            except Exception as e:
                _logger.exception("Unified PDF build failed for %s: %s", order.name, e)
                raise UserError(_("Failed to build unified PDF for %s: %s") % (order.display_name, e))

        return result
