from odoo import models, _
import io, base64, logging, re
from odoo.tools import pdf
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
_PDF_EXT_RE = re.compile(r'\.pdf$', re.I)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        collected = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)

        report = self._get_report(report_ref)
        # Solo intervenir en el reporte estándar de cotización
        if report.report_name != 'sale.report_saleorder':
            return collected

        orders = self.env['sale.order'].sudo().browse(res_ids or [])
        for order in orders:
            if not order.exists():
                continue

            # Debe estar habilitado en el equipo
            if not getattr(order, 'team_include_technical_proposal', False):
                continue

            try:
                streams = []

                # 1) Header (binario en crm.team)
                header_b64 = order.team_id.sudo().trscma_proposal_header_pdf_tr
                if header_b64:
                    streams.append(base64.b64decode(header_b64))

                # 2) Cotización base (lo que ya generó Odoo)
                if order.id in collected:
                    streams.append(collected[order.id]['stream'].getvalue())
                else:
                    base_pdf, _ = report.sudo()._render_qweb_pdf(res_ids=[order.id])
                    streams.append(base_pdf)

                # 3) Alcances (si existen)
                if getattr(order, 'related_scope_ids', False):
                    scope_report = self.env.ref('treming_scope_management.action_report_scope_proposal').sudo()
                    # Si quieres forzar el paperformat de la compañía, descomenta:
                    # paperformat = order.company_id.sudo().paperformat_id
                    # if paperformat:
                    #     scope_report.write({'paperformat_id': paperformat.id})
                    scope_pdf, _ = scope_report._render_qweb_pdf(res_ids=[order.id])
                    streams.append(scope_pdf)

                # 4) Adjuntos PDF del Sales Team (excluir binarios de header/footer para no duplicar)
                if order.team_id:
                    domain = [
                        ('res_model', '=', 'crm.team'),
                        ('res_id', '=', order.team_id.id),
                        ('res_field', 'not in', ['trscma_proposal_header_pdf_tr', 'trscma_proposal_footer_pdf_tr']),
                    ]
                    # mimetype sometimes empty; acepta mimetype 'pdf' o nombre .pdf
                    team_atts = self.env['ir.attachment'].sudo().search(domain, order='id')
                    for att in team_atts:
                        mt = (att.mimetype or '').lower()
                        if (mt == 'application/pdf') or ('pdf' in mt) or _PDF_EXT_RE.search(att.name or ''):
                            if att.datas:
                                streams.append(base64.b64decode(att.datas))

                # 5) Footer (binario en crm.team)
                footer_b64 = order.team_id.sudo().trscma_proposal_footer_pdf_tr
                if footer_b64:
                    streams.append(base64.b64decode(footer_b64))

                # Fusiona por pedido
                if streams:
                    merged = pdf.merge_pdf(streams)
                    collected[order.id]['stream'] = io.BytesIO(merged)

            except Exception as e:
                _logger.exception("Unified PDF build failed for %s", order.name)
                raise UserError(_("Failed to build unified PDF for %s: %s") % (order.display_name, e))

        return collected
