from datetime import datetime, time, timedelta

from markupsafe import Markup, escape

from odoo import api, fields, models


class PrimetechInterAgencyTransferDashboard(models.Model):
    _name = "primetech.inter.agency.transfer.dashboard"
    _description = "Tableau de bord des transferts PrimeTech"

    name = fields.Char(default="Tableau de bord", readonly=True)
    dashboard_html = fields.Html(compute="_compute_dashboard_html", sanitize=False)

    def _count(self, domain):
        return self.env["primetech.inter.agency.transfer"].search_count(domain)

    def _sum(self, field_name, domain=None):
        transfers = self.env["primetech.inter.agency.transfer"].search(domain or [])
        return sum(transfers.mapped(field_name))

    def _action_url(self, xmlid):
        action = self.env.ref(xmlid, raise_if_not_found=False)
        if not action:
            return "#"
        return f"/web#action={action.id}"

    def _weekly_activity_chart(self):
        """Build a seven-day chart, scoped by the user's record rules."""
        today = fields.Date.context_today(self)
        first_day = today - timedelta(days=6)
        start = datetime.combine(first_day, time.min)
        transfers = self.env["primetech.inter.agency.transfer"].search(
            [("request_date", ">=", fields.Datetime.to_string(start))]
        )
        counts = {first_day + timedelta(days=offset): 0 for offset in range(7)}
        for transfer in transfers:
            request_day = fields.Datetime.context_timestamp(self, transfer.request_date).date()
            if request_day in counts:
                counts[request_day] += 1

        values = list(counts.values())
        peak = max(values) or 1
        points = []
        labels = []
        for index, (day, value) in enumerate(counts.items()):
            x = index * (640 / 6)
            y = 178 - (value / peak * 130)
            points.append(f"{x:.0f},{y:.0f}")
            plural = "s" if value != 1 else ""
            labels.append(f'<span><strong>{day.strftime("%d/%m")}</strong><small>{value} transfert{plural}</small></span>')
        return " ".join(points), "".join(labels), sum(values)

    def _role_label(self):
        user = self.env.user
        if user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_administrator"):
            return "Administrateur"
        if user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_logistics_manager"):
            return "Responsable logistique"
        if user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_manager"):
            return "Gestionnaire"
        if user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_warehouseman"):
            return "Magasinier"
        return "Utilisateur"

    @api.model
    def get_dashboard_html(self):
        """Payload consumed by the client-action dashboard."""
        dashboard = self.search([], limit=1)
        return str(dashboard.dashboard_html or "")

    @api.depends_context("uid", "allowed_company_ids")
    def _compute_dashboard_html(self):
        for dashboard in self:
            user = dashboard.env.user
            can_operate = user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_warehouseman")
            can_manage = user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_manager")
            can_analyze = (
                user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_logistics_manager")
                or user.has_group("primetech_inter_agency_transfer.group_primetech_transfer_administrator")
            )

            total = dashboard._count([])
            to_prepare = dashboard._count([("state", "in", ["draft", "waiting_preparation", "preparing"])])
            to_ship = dashboard._count([("state", "=", "ready")])
            in_transit = dashboard._count([("state", "=", "in_transit")])
            to_receive = dashboard._count([("state", "=", "waiting_reception")])
            done = dashboard._count([("state", "in", ["done", "returned"])])
            discrepancies = dashboard._count([("state", "=", "discrepancy")])
            cancelled = dashboard._count([("state", "=", "cancelled")])
            internal = dashboard._count([("transfer_type", "=", "internal")])
            inter_agency = dashboard._count([("transfer_type", "=", "inter_agency")])
            high_priority = dashboard._count([("priority", "in", ["1", "2"])])
            normal_priority = dashboard._count([("priority", "=", "0")])
            requested_qty = dashboard._sum("total_requested_qty")
            shipped_qty = dashboard._sum("total_shipped_qty")
            received_qty = dashboard._sum("total_received_qty")
            total_value = dashboard._sum("total_value")
            reception_rate = received_qty / shipped_qty * 100.0 if shipped_qty else 0.0
            inter_agency_rate = inter_agency / total * 100.0 if total else 0.0
            internal_rate = internal / total * 100.0 if total else 0.0
            high_priority_rate = high_priority / total * 100.0 if total else 0.0
            normal_priority_rate = normal_priority / total * 100.0 if total else 0.0
            weekly_points, weekly_labels, weekly_total = dashboard._weekly_activity_chart()

            company_tags = "".join(
                f'<span class="o_pt_tag">{escape(company.name)}</span>' for company in user.company_ids[:5]
            ) or '<span class="o_pt_tag">Aucune société</span>'
            role_label = escape(dashboard._role_label())
            user_name = escape(user.name)
            url_all = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer")
            url_new = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_new")
            url_prepare = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_to_prepare")
            url_ship = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_to_ship")
            url_receive = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_to_receive")
            url_in_transit = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_in_transit")
            url_discrepancies = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_discrepancies")
            url_done = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_done")
            url_analysis = dashboard._action_url("primetech_inter_agency_transfer.action_primetech_transfer_dashboard")

            operational_items = ""
            quick_cards = ""
            if can_operate or can_manage or can_analyze:
                operational_items += f"""
                    <li><a href="{url_prepare}"><span class="o_pt_notice_icon o_pt_notice_blue">✓</span><div><strong>{to_prepare} bons à préparer</strong><small>Préparation attendue à l'agence source</small></div><em>{to_prepare}</em></a></li>
                    <li><a href="{url_ship}"><span class="o_pt_notice_icon o_pt_notice_green">↗</span><div><strong>{to_ship} bons à expédier</strong><small>Prêts pour validation / expédition</small></div><em>{to_ship}</em></a></li>
                    <li><a href="{url_receive}"><span class="o_pt_notice_icon o_pt_notice_orange">↘</span><div><strong>{to_receive} réceptions en attente</strong><small>Actions attendues à destination</small></div><em>{to_receive}</em></a></li>
                """
                quick_cards += f"""
                    <a class="o_pt_quick_card" href="{url_new}"><span>＋</span><strong>Nouveau transfert</strong><small>Créer un bon</small></a>
                    <a class="o_pt_quick_card" href="{url_prepare}"><span>✓</span><strong>À préparer</strong><small>Voir la liste</small></a>
                    <a class="o_pt_quick_card" href="{url_ship}"><span>🚚</span><strong>À expédier</strong><small>Voir la liste</small></a>
                    <a class="o_pt_quick_card" href="{url_receive}"><span>↘</span><strong>À réceptionner</strong><small>Voir la liste</small></a>
                """
            if can_manage or can_analyze:
                operational_items += f"""
                    <li><a href="{url_discrepancies}"><span class="o_pt_notice_icon o_pt_notice_purple">!</span><div><strong>{discrepancies} transferts avec écarts</strong><small>Contrôle et régularisation nécessaires</small></div><em>{discrepancies}</em></a></li>
                """
                quick_cards += f"""
                    <a class="o_pt_quick_card" href="{url_discrepancies}"><span>!</span><strong>Avec écarts</strong><small>Voir la liste</small></a>
                    <a class="o_pt_quick_card" href="{url_done}"><span>📄</span><strong>Rapports</strong><small>Imprimer / générer</small></a>
                """
            if can_analyze:
                quick_cards += f"""
                    <a class="o_pt_quick_card" href="{url_analysis}"><span>▥</span><strong>Tableau d'analyse</strong><small>Accéder</small></a>
                    <a class="o_pt_quick_card" href="{url_analysis}"><span>⚙</span><strong>Paramètres</strong><small>Configurer</small></a>
                """
            if not operational_items:
                operational_items = "<li><span class=\"o_pt_notice_icon\">0</span><div><strong>Aucune action disponible</strong><small>Votre profil n'a pas d'action directe à traiter.</small></div><em>0</em></li>"
            if not quick_cards:
                quick_cards = "<div class=\"o_pt_quick_card\"><span>🔒</span><strong>Accès limité</strong><small>Contactez votre responsable</small></div>"

            analysis_panels = ""
            if can_manage or can_analyze:
                analysis_panels = f"""
                    <a class="o_pt_panel o_pt_chart_panel o_pt_span_2 o_pt_clickable_panel" href="{url_analysis}">
                        <div class="o_pt_panel_head"><h2>Évolution des transferts</h2><span>{weekly_total} sur 7 jours</span></div>
                        <svg class="o_pt_line_chart" viewBox="0 0 640 220" preserveAspectRatio="none">
                            <polyline points="{weekly_points}"/>
                        </svg>
                        <div class="o_pt_chart_labels">{weekly_labels}</div>
                    </a>
                    <a class="o_pt_panel o_pt_clickable_panel" href="{url_analysis}">
                        <h2>Transferts par type</h2>
                        <div class="o_pt_donut" style="--value:{inter_agency_rate:.0f};"><strong>{total}</strong><span>Total</span></div>
                        <div class="o_pt_split"><span>Inter-agences</span><strong>{inter_agency} ({inter_agency_rate:.0f}%)</strong></div>
                        <div class="o_pt_split"><span>Inter-entrepôts</span><strong>{internal} ({internal_rate:.0f}%)</strong></div>
                    </a>
                    <a class="o_pt_panel o_pt_clickable_panel" href="{url_analysis}">
                        <h2>Priorité des transferts</h2>
                        <div class="o_pt_donut o_pt_donut_priority" style="--value:{high_priority_rate:.0f};"><strong>{total}</strong><span>Total</span></div>
                        <div class="o_pt_split"><span>Haute / urgente</span><strong>{high_priority} ({high_priority_rate:.0f}%)</strong></div>
                        <div class="o_pt_split"><span>Normale</span><strong>{normal_priority} ({normal_priority_rate:.0f}%)</strong></div>
                    </a>
                """

            html = f"""
                <div class="o_pt_home_dashboard o_pt_home_dashboard_modern">
                    <div class="o_pt_panel o_pt_span_full o_pt_quick_top">
                        <div class="o_pt_panel_head"><h2>Actions rapides</h2><span>Accès direct</span></div>
                        <div class="o_pt_quick_grid">{quick_cards}</div>
                    </div>
                    <div class="o_pt_kpi_grid o_pt_modern_kpis">
                        <a class="o_pt_kpi" href="{url_all}"><span>Total transferts</span><strong>{total}</strong><small>↗ Documents visibles</small></a>
                        <a class="o_pt_kpi" href="{url_prepare}"><span>À préparer</span><strong>{to_prepare}</strong><small>Magasin source</small></a>
                        <a class="o_pt_kpi" href="{url_in_transit}"><span>En transit</span><strong>{in_transit}</strong><small>Suivi livraison</small></a>
                        <a class="o_pt_kpi" href="{url_receive}"><span>À réceptionner</span><strong>{to_receive}</strong><small>Magasin destination</small></a>
                        <a class="o_pt_kpi" href="{url_done}"><span>Terminés</span><strong>{done}</strong><small>Inclut les retours</small></a>
                        <a class="o_pt_kpi o_pt_kpi_rate" href="{url_done}"><span>Taux réception complète</span><strong>{reception_rate:.0f}%</strong><small>{received_qty:.0f} / {shipped_qty:.0f}</small></a>
                    </div>
                    <div class="o_pt_modern_grid">
                        {analysis_panels}
                        <div class="o_pt_panel o_pt_notifications">
                            <div class="o_pt_panel_head"><h2>Centre de notifications</h2><span>{to_ship + to_receive + discrepancies}</span></div>
                            <ul>{operational_items}</ul>
                        </div>
                        <div class="o_pt_panel o_pt_access_panel">
                            <div class="o_pt_panel_head"><h2>Mon accès</h2><span>{role_label}</span></div>
                            <div class="o_pt_access_block"><strong>Sociétés autorisées</strong><div>{company_tags}</div></div>
                            <div class="o_pt_access_block"><strong>Rôle actuel</strong><div><span class="o_pt_tag o_pt_tag_role">{role_label}</span></div></div>
                        </div>
                        <div class="o_pt_footer_note o_pt_span_full">🛡️ Données visibles selon vos sociétés et niveaux d'accès · Quantité demandée : {requested_qty:.0f} · Quantité expédiée : {shipped_qty:.0f} · Quantité reçue : {received_qty:.0f} · Annulés : {cancelled} · Valeur : {total_value:,.0f}</div>
                    </div>
                </div>
            """
            dashboard.dashboard_html = Markup(html)

    def _open_transfers(self, name, domain):
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": "primetech.inter.agency.transfer",
            "view_mode": "list,kanban,form,pivot,graph",
            "domain": domain,
            "context": {"search_default_group_state": 1},
        }

    def action_open_to_prepare(self):
        return self._open_transfers("À préparer", [("state", "in", ["draft", "waiting_preparation", "preparing"])])

    def action_open_to_ship(self):
        return self._open_transfers("À expédier / valider", [("state", "=", "ready")])

    def action_open_to_receive(self):
        return self._open_transfers("À réceptionner", [("state", "in", ["in_transit", "waiting_reception"])])

    def action_open_discrepancies(self):
        return self._open_transfers("Écarts à traiter", [("state", "=", "discrepancy")])

    def action_open_done(self):
        return self._open_transfers("Terminés / faits", [("state", "in", ["done", "returned"])])

    def action_open_analysis(self):
        return self.env.ref("primetech_inter_agency_transfer.action_primetech_transfer_dashboard").read()[0]
