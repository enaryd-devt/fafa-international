from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PrimetechInterAgencyTransfer(models.Model):
    _name = "primetech.inter.agency.transfer"
    _description = "Transfert inter-agences PrimeTech"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(string="Référence", default="Nouveau", copy=False, readonly=True, tracking=True)
    transfer_type = fields.Selection(
        [("inter_agency", "Inter-agences"), ("internal", "Transfert interne entre entrepôts")],
        string="Type de transfert",
        required=True,
        default="inter_agency",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Brouillon"), ("confirmed", "Confirmé"),
            ("waiting_preparation", "En attente de préparation"), ("preparing", "En préparation"),
            ("ready", "Prêt à expédier"), ("shipped", "Expédié"),
            ("in_transit", "En transit"), ("waiting_reception", "En attente de réception"),
            ("partial_reception", "Réception partielle"), ("discrepancy", "Avec écart"),
            ("received", "Reçu"), ("done", "Terminé"), ("rejected", "Refusé"),
            ("cancelled", "Annulé"), ("returned", "Retourné"),
        ],
        string="Statut",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one("res.company", string="Société", required=True, default=lambda self: self.env.company, index=True)
    source_agency_id = fields.Many2one("res.company", string="Société émettrice", required=True, tracking=True)
    source_warehouse_id = fields.Many2one("stock.warehouse", string="Entrepôt émetteur", required=True)
    source_warehouse_location_id = fields.Many2one(related="source_warehouse_id.lot_stock_id")
    source_allowed_location_ids = fields.Many2many(
        "stock.location",
        "primetech_transfer_source_allowed_location_rel",
        "transfer_id",
        "location_id",
        compute="_compute_allowed_location_ids",
    )
    source_location_id = fields.Many2one("stock.location", string="Emplacement source", required=True)
    destination_agency_id = fields.Many2one("res.company", string="Société réceptrice", required=True, tracking=True)
    destination_warehouse_id = fields.Many2one("stock.warehouse", string="Entrepôt récepteur", required=True)
    destination_warehouse_location_id = fields.Many2one(related="destination_warehouse_id.lot_stock_id")
    destination_allowed_location_ids = fields.Many2many(
        "stock.location",
        "primetech_transfer_destination_allowed_location_rel",
        "transfer_id",
        "location_id",
        compute="_compute_allowed_location_ids",
    )
    destination_location_id = fields.Many2one("stock.location", string="Emplacement destination", required=True)
    transit_location_id = fields.Many2one("stock.location", string="Emplacement de transit")
    manager_id = fields.Many2one("res.users", string="Gestionnaire", required=True, default=lambda self: self.env.user, check_company=True)
    source_warehouseman_id = fields.Many2one("res.users", string="Magasinier expéditeur", check_company=True)
    destination_warehouseman_id = fields.Many2one("res.users", string="Magasinier réceptionnaire", check_company=True)
    request_date = fields.Datetime(string="Date de demande", default=fields.Datetime.now, required=True, tracking=True)
    planned_shipping_date = fields.Datetime(string="Date prévue d'expédition", tracking=True)
    actual_shipping_date = fields.Datetime(string="Date réelle d'expédition", readonly=True, tracking=True)
    planned_reception_date = fields.Datetime(string="Date prévue de réception", tracking=True)
    actual_reception_date = fields.Datetime(string="Date réelle de réception", readonly=True, tracking=True)
    priority = fields.Selection([("0", "Normale"), ("1", "Haute"), ("2", "Urgente")], string="Priorité", default="0", required=True)
    reason = fields.Char(string="Motif")
    note = fields.Html(string="Notes")
    line_ids = fields.One2many("primetech.inter.agency.transfer.line", "transfer_id", string="Produits", copy=True)
    outgoing_picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    incoming_picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    internal_picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    picking_ids = fields.One2many("stock.picking", "primetech_transfer_id", readonly=True)
    total_product_count = fields.Integer(compute="_compute_totals", store=True)
    total_requested_qty = fields.Float(compute="_compute_totals", store=True, digits="Product Unit of Measure")
    total_prepared_qty = fields.Float(compute="_compute_totals", store=True, digits="Product Unit of Measure")
    total_shipped_qty = fields.Float(compute="_compute_totals", store=True, digits="Product Unit of Measure")
    total_received_qty = fields.Float(compute="_compute_totals", store=True, digits="Product Unit of Measure")
    total_value = fields.Monetary(compute="_compute_totals", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="company_id.currency_id")
    discrepancy_count = fields.Integer(compute="_compute_totals", store=True)
    preparation_progress = fields.Float(compute="_compute_totals", store=True)
    shipment_progress = fields.Float(compute="_compute_totals", store=True)
    reception_progress = fields.Float(compute="_compute_totals", store=True)
    is_inter_agency = fields.Boolean(compute="_compute_transfer_kind")
    is_internal_transfer = fields.Boolean(compute="_compute_transfer_kind")
    transport_mode = fields.Selection([( "road", "Routier"), ("rail", "Ferroviaire"), ("air", "Aérien"), ("sea", "Maritime"), ("other", "Autre")], string="Mode de transport")
    carrier_name = fields.Char(string="Transporteur")
    driver_name = fields.Char(string="Chauffeur")
    driver_phone = fields.Char(string="Téléphone du chauffeur")
    vehicle_name = fields.Char(string="Véhicule")
    vehicle_registration = fields.Char(string="Immatriculation")
    package_count = fields.Integer(string="Nombre de colis")
    total_weight = fields.Float(string="Poids total")
    departure_datetime = fields.Datetime(string="Date de départ")
    expected_arrival_datetime = fields.Datetime(string="Arrivée prévue")
    actual_arrival_datetime = fields.Datetime(string="Arrivée réelle", readonly=True)
    transport_reference = fields.Char(string="Référence de transport")
    transport_note = fields.Text(string="Note de transport")

    @api.depends("line_ids.requested_qty", "line_ids.prepared_qty", "line_ids.shipped_qty", "line_ids.received_qty", "line_ids.total_cost", "line_ids.difference_qty")
    def _compute_totals(self):
        for transfer in self:
            transfer.total_product_count = len(transfer.line_ids)
            transfer.total_requested_qty = sum(transfer.line_ids.mapped("requested_qty"))
            transfer.total_prepared_qty = sum(transfer.line_ids.mapped("prepared_qty"))
            transfer.total_shipped_qty = sum(transfer.line_ids.mapped("shipped_qty"))
            transfer.total_received_qty = sum(transfer.line_ids.mapped("received_qty"))
            transfer.total_value = sum(transfer.line_ids.mapped("total_cost"))
            transfer.discrepancy_count = len(transfer.line_ids.filtered(lambda line: line.difference_qty))
            transfer.preparation_progress = (transfer.total_prepared_qty / transfer.total_requested_qty * 100.0) if transfer.total_requested_qty else 0.0
            transfer.shipment_progress = (transfer.total_shipped_qty / transfer.total_requested_qty * 100.0) if transfer.total_requested_qty else 0.0
            transfer.reception_progress = (transfer.total_received_qty / transfer.total_requested_qty * 100.0) if transfer.total_requested_qty else 0.0

    @api.depends("transfer_type")
    def _compute_transfer_kind(self):
        for transfer in self:
            transfer.is_inter_agency = transfer.transfer_type == "inter_agency"
            transfer.is_internal_transfer = transfer.transfer_type == "internal"

    def _get_warehouse_location_root(self, warehouse):
        if not warehouse:
            return self.env["stock.location"]
        if warehouse.view_location_id:
            return warehouse.view_location_id
        if warehouse.lot_stock_id.location_id:
            return warehouse.lot_stock_id.location_id
        return warehouse.lot_stock_id

    @api.depends(
        "source_warehouse_id.view_location_id",
        "source_warehouse_id.lot_stock_id",
        "destination_warehouse_id.view_location_id",
        "destination_warehouse_id.lot_stock_id",
    )
    def _compute_allowed_location_ids(self):
        StockLocation = self.env["stock.location"]
        for transfer in self:
            transfer.source_allowed_location_ids = StockLocation
            transfer.destination_allowed_location_ids = StockLocation
            source_root_location = transfer._get_warehouse_location_root(transfer.source_warehouse_id)
            destination_root_location = transfer._get_warehouse_location_root(transfer.destination_warehouse_id)
            if source_root_location:
                transfer.source_allowed_location_ids = StockLocation.search([
                    ("id", "child_of", source_root_location.id),
                    ("usage", "=", "internal"),
                ])
            if destination_root_location:
                transfer.destination_allowed_location_ids = StockLocation.search([
                    ("id", "child_of", destination_root_location.id),
                    ("usage", "=", "internal"),
                ])

    @api.onchange("transfer_type", "company_id")
    def _onchange_transfer_type_company_id(self):
        if self.transfer_type == "internal":
            self.source_agency_id = self.company_id
            self.destination_agency_id = self.company_id
            self.source_warehouse_id = False
            self.source_location_id = False
            self.destination_warehouse_id = False
            self.destination_location_id = False
            company_domain = [("company_id", "=", self.company_id.id)] if self.company_id else [("id", "=", False)]
            return {
                "domain": {
                    "source_warehouse_id": company_domain,
                    "destination_warehouse_id": company_domain,
                    "source_location_id": [("id", "=", False)],
                    "destination_location_id": [("id", "=", False)],
                }
            }
        return {"domain": {}}

    @api.onchange("source_agency_id")
    def _onchange_source_agency_id(self):
        self.source_warehouse_id = False
        self.source_location_id = False
        warehouse_domain = [("id", "=", False)]
        if self.source_agency_id:
            warehouse_domain = [("company_id", "=", self.source_agency_id.id)]
        return {"domain": {"source_warehouse_id": warehouse_domain, "source_location_id": [("id", "=", False)]}}

    @api.onchange("destination_agency_id")
    def _onchange_destination_agency_id(self):
        self.destination_warehouse_id = False
        self.destination_location_id = False
        warehouse_domain = [("id", "=", False)]
        if self.destination_agency_id:
            warehouse_domain = [("company_id", "=", self.destination_agency_id.id)]
        return {"domain": {"destination_warehouse_id": warehouse_domain, "destination_location_id": [("id", "=", False)]}}

    @api.onchange("source_warehouse_id")
    def _onchange_source_warehouse_id(self):
        self.source_location_id = False
        location_domain = [("id", "=", False)]
        if self._get_warehouse_location_root(self.source_warehouse_id):
            location_domain = [("id", "in", self.source_allowed_location_ids.ids)]
        return {"domain": {"source_location_id": location_domain}}

    @api.onchange("destination_warehouse_id")
    def _onchange_destination_warehouse_id(self):
        self.destination_location_id = False
        location_domain = [("id", "=", False)]
        if self._get_warehouse_location_root(self.destination_warehouse_id):
            location_domain = [("id", "in", self.destination_allowed_location_ids.ids)]
        return {"domain": {"destination_location_id": location_domain}}

    @api.onchange("source_location_id")
    def _onchange_source_location_id(self):
        self.line_ids._refresh_stock_quantities()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("transfer_type") == "internal":
                company_id = vals.get("company_id") or self.env.company.id
                vals.setdefault("source_agency_id", company_id)
                vals.setdefault("destination_agency_id", company_id)
            if vals.get("name", _("Nouveau")) == _("Nouveau"):
                transfer_type = vals.get("transfer_type", "inter_agency")
                sequence_code = f"primetech.inter.agency.transfer.{transfer_type}"
                vals["name"] = self.env["ir.sequence"].next_by_code(sequence_code) or _("Nouveau")
        return super().create(vals_list)

    def _ensure_action_allowed(self, allowed_states):
        invalid_transfers = self.filtered(lambda transfer: transfer.state not in allowed_states)
        if invalid_transfers:
            raise UserError(_("L'action n'est pas autorisée dans l'état actuel du bon de transfert."))

    def _ensure_transfer_lines(self):
        for transfer in self:
            if not transfer.line_ids:
                raise UserError(_("Ajoutez au moins une ligne de produit avant de continuer."))
            invalid_lines = transfer.line_ids.filtered(lambda line: not line.product_id or line.requested_qty <= 0)
            if invalid_lines:
                raise UserError(_("Chaque ligne doit contenir un produit et une quantité demandée strictement positive."))

    def _get_transfer_picking_type(self):
        self.ensure_one()
        picking_type = self.source_warehouse_id.int_type_id
        if not picking_type:
            raise UserError(_("Configurez un type d'opération interne sur l'entrepôt émetteur."))
        return picking_type

    def _get_transit_location(self):
        self.ensure_one()
        if self.transit_location_id:
            return self.transit_location_id
        transit_location = self.env["stock.location"].search([
            ("usage", "=", "transit"),
            ("company_id", "=", False),
        ], limit=1)
        if not transit_location:
            transit_location = self.env["stock.location"].sudo().create({
                "name": _("Transit PrimeTech"),
                "usage": "transit",
                "company_id": False,
            })
        self.transit_location_id = transit_location
        return transit_location

    def _get_stock_picking(self, operation="outgoing"):
        self.ensure_one()
        if self.transfer_type == "internal":
            picking = self.internal_picking_id
            picking_company = self.source_agency_id
            source_location = self.source_location_id
            destination_location = self.destination_location_id
            warehouse = self.source_warehouse_id
        elif operation == "incoming":
            picking = self.incoming_picking_id
            picking_company = self.destination_agency_id
            source_location = self._get_transit_location()
            destination_location = self.destination_location_id
            warehouse = self.destination_warehouse_id
        else:
            picking = self.outgoing_picking_id
            picking_company = self.source_agency_id
            source_location = self.source_location_id
            destination_location = self._get_transit_location()
            warehouse = self.source_warehouse_id
        if picking:
            return picking
        picking_type = warehouse.int_type_id
        if not picking_type:
            raise UserError(_("Configurez un type d'opération interne sur l'entrepôt %s.") % warehouse.display_name)
        picking = self.env["stock.picking"].with_company(picking_company).create({
            "picking_type_id": picking_type.id,
            "location_id": source_location.id,
            "location_dest_id": destination_location.id,
            "origin": self.name,
            "company_id": picking_company.id,
            "primetech_transfer_id": self.id,
        })
        if self.transfer_type == "internal":
            self.internal_picking_id = picking
        elif operation == "incoming":
            self.incoming_picking_id = picking
        else:
            self.outgoing_picking_id = picking
        return picking

    def _sync_stock_moves(self, operation="outgoing"):
        StockMove = self.env["stock.move"]
        for transfer in self:
            picking = transfer._get_stock_picking(operation=operation)
            existing_moves = {move.primetech_transfer_line_id.id: move for move in picking.move_ids_without_package}
            for line in transfer.line_ids:
                quantity = line.requested_qty
                if operation == "incoming":
                    quantity = line.received_qty or line.shipped_qty
                elif line.prepared_qty:
                    quantity = line.prepared_qty
                move_values = {
                    "name": line.product_id.display_name,
                    "product_id": line.product_id.id,
                    "product_uom": line.product_uom_id.id,
                    "product_uom_qty": quantity,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "picking_id": picking.id,
                    "company_id": picking.company_id.id,
                    "primetech_transfer_line_id": line.id,
                }
                move = existing_moves.get(line.id)
                if move and move.state not in ("done", "cancel"):
                    move.write(move_values)
                elif not move:
                    StockMove.with_company(picking.company_id).create(move_values)
            obsolete_moves = picking.move_ids_without_package.filtered(
                lambda move: move.primetech_transfer_line_id and move.primetech_transfer_line_id not in transfer.line_ids and move.state not in ("done", "cancel")
            )
            obsolete_moves.unlink()
            if picking.state == "draft":
                picking.action_confirm()

    def _set_picking_done_quantities(self, picking, quantity_by_product):
        for move in picking.move_ids_without_package.filtered(lambda stock_move: stock_move.state not in ("done", "cancel")):
            key = move.primetech_transfer_line_id.id or move.product_id.id
            quantity = quantity_by_product.get(key, 0.0)
            if "quantity_done" in move._fields:
                move.quantity_done = quantity
            elif "quantity" in move._fields:
                move.quantity = quantity
            for move_line in move.move_line_ids:
                if "quantity" in move_line._fields:
                    move_line.quantity = quantity
                elif "qty_done" in move_line._fields:
                    move_line.qty_done = quantity

    def _validate_picking(self, picking, quantity_field):
        quantity_by_line = {
            line.id: line[quantity_field]
            for line in self.line_ids
            if line[quantity_field] > 0
        }
        if not quantity_by_line:
            raise UserError(_("Aucune quantité n'est renseignée pour valider l'opération."))
        if picking.state == "draft":
            picking.action_confirm()
        picking.action_assign()
        self._set_picking_done_quantities(picking, quantity_by_line)
        picking.with_context(skip_immediate=True, skip_backorder=True, cancel_backorder=True).button_validate()

    def action_confirm(self):
        self._ensure_action_allowed(("draft",))
        self._ensure_transfer_lines()
        self.line_ids._refresh_stock_quantities()
        self.write({"state": "waiting_preparation"})
        return True

    def action_prepare(self):
        self._ensure_action_allowed(("confirmed", "waiting_preparation", "preparing"))
        self._ensure_transfer_lines()
        policy = self.env["ir.config_parameter"].sudo().get_param(
            "primetech_inter_agency_transfer.insufficient_stock_policy", "block"
        )
        for transfer in self:
            transfer.line_ids._refresh_stock_quantities()
            insufficient_lines = transfer.line_ids.filtered(lambda line: line.requested_qty > line.available_qty)
            if insufficient_lines and policy == "block":
                product_names = ", ".join(insufficient_lines.mapped("product_id.display_name"))
                raise UserError(_("Stock insuffisant pour : %s") % product_names)
            for line in transfer.line_ids:
                line.prepared_qty = min(line.requested_qty, line.available_qty) if policy == "block" else line.requested_qty
                line.line_state = "prepared"
            transfer._sync_stock_moves()
            picking = transfer._get_stock_picking(operation="outgoing")
            picking.action_assign()
            transfer.state = "ready"
        return True

    def action_ship(self):
        self._ensure_action_allowed(("ready",))
        for transfer in self:
            lines_without_preparation = transfer.line_ids.filtered(lambda line: line.prepared_qty <= 0)
            if lines_without_preparation:
                raise UserError(_("Préparez les quantités avant l'expédition."))
            transfer._sync_stock_moves()
            picking = transfer._get_stock_picking(operation="outgoing")
            transfer._validate_picking(picking, "prepared_qty")
            transfer.line_ids.write({"line_state": "shipped"})
            for line in transfer.line_ids:
                line.shipped_qty = line.prepared_qty
            transfer.write({
                "actual_shipping_date": fields.Datetime.now(),
                "actual_reception_date": fields.Datetime.now() if transfer.transfer_type == "internal" else False,
                "state": "done" if transfer.transfer_type == "internal" else "in_transit",
            })
        return True

    def action_mark_waiting_reception(self):
        self._ensure_action_allowed(("in_transit",))
        self.write({"state": "waiting_reception"})
        return True

    def action_receive(self):
        self._ensure_action_allowed(("in_transit", "waiting_reception"))
        for transfer in self:
            for line in transfer.line_ids:
                if not line.received_qty:
                    line.received_qty = line.shipped_qty
                line.line_state = "received" if not line.difference_qty else "discrepancy"
            if transfer.transfer_type == "inter_agency":
                transfer._sync_stock_moves(operation="incoming")
                incoming_picking = transfer._get_stock_picking(operation="incoming")
                transfer._validate_picking(incoming_picking, "received_qty")
            transfer.write({
                "actual_reception_date": fields.Datetime.now(),
                "state": "discrepancy" if transfer.discrepancy_count else "done",
            })
        return True

    def action_cancel(self):
        for transfer in self:
            (transfer.outgoing_picking_id | transfer.incoming_picking_id | transfer.internal_picking_id).filtered(
                lambda picking: picking.state not in ("done", "cancel")
            ).action_cancel()
            transfer.state = "cancelled"
        return True

    def action_print_transfer(self):
        return self.env.ref("primetech_inter_agency_transfer.action_report_primetech_transfer").report_action(self)

    def action_return(self):
        self._ensure_action_allowed(("done", "discrepancy"))
        for transfer in self:
            return_transfer = self.create({
                "transfer_type": transfer.transfer_type,
                "source_agency_id": transfer.destination_agency_id.id,
                "source_warehouse_id": transfer.destination_warehouse_id.id,
                "source_location_id": transfer.destination_location_id.id,
                "destination_agency_id": transfer.source_agency_id.id,
                "destination_warehouse_id": transfer.source_warehouse_id.id,
                "destination_location_id": transfer.source_location_id.id,
                "reason": _("Retour du bon %s") % transfer.name,
                "line_ids": [(0, 0, {
                    "product_id": line.product_id.id,
                    "requested_qty": line.received_qty or line.shipped_qty or line.requested_qty,
                }) for line in transfer.line_ids],
            })
            transfer.message_post(body=_("Bon de retour créé : %s") % return_transfer.display_name)
            transfer.state = "returned"
        return True

    def action_reset_to_draft(self):
        self._ensure_action_allowed(("cancelled",))
        self.write({"state": "draft"})
        return True

    @api.constrains("transfer_type", "source_agency_id", "destination_agency_id", "source_location_id", "destination_location_id")
    def _check_transfer_locations(self):
        for transfer in self:
            if transfer.source_location_id == transfer.destination_location_id:
                raise ValidationError(_("Les emplacements source et destination doivent être différents."))
            if transfer.transfer_type == "inter_agency" and transfer.source_agency_id == transfer.destination_agency_id:
                raise ValidationError(_("Un transfert inter-agences requiert deux agences différentes."))
            if transfer.transfer_type == "internal" and transfer.source_agency_id != transfer.destination_agency_id:
                raise ValidationError(_("Un transfert interne requiert la même agence source et destination."))

    @api.constrains(
        "source_agency_id",
        "source_warehouse_id",
        "source_location_id",
        "destination_agency_id",
        "destination_warehouse_id",
        "destination_location_id",
    )
    def _check_agency_resources(self):
        for transfer in self:
            if transfer.source_warehouse_id.company_id != transfer.source_agency_id:
                raise ValidationError(_("L'entrepôt émetteur doit appartenir à la société émettrice."))
            if transfer.destination_warehouse_id.company_id != transfer.destination_agency_id:
                raise ValidationError(_("L'entrepôt récepteur doit appartenir à la société réceptrice."))
            if transfer.source_location_id.company_id and transfer.source_location_id.company_id != transfer.source_agency_id:
                raise ValidationError(_("L'emplacement source doit appartenir à la société émettrice."))
            if transfer.destination_location_id.company_id and transfer.destination_location_id.company_id != transfer.destination_agency_id:
                raise ValidationError(_("L'emplacement destination doit appartenir à la société réceptrice."))
            source_root_location = transfer._get_warehouse_location_root(transfer.source_warehouse_id)
            if source_root_location and transfer.source_location_id:
                allowed_source_locations = self.env["stock.location"].search([
                    ("id", "child_of", source_root_location.id),
                ])
                if transfer.source_location_id not in allowed_source_locations:
                    raise ValidationError(_("L'emplacement source doit appartenir à l'entrepôt émetteur."))
            destination_root_location = transfer._get_warehouse_location_root(transfer.destination_warehouse_id)
            if destination_root_location and transfer.destination_location_id:
                allowed_destination_locations = self.env["stock.location"].search([
                    ("id", "child_of", destination_root_location.id),
                ])
                if transfer.destination_location_id not in allowed_destination_locations:
                    raise ValidationError(_("L'emplacement destination doit appartenir à l'entrepôt récepteur."))


class PrimetechInterAgencyTransferLine(models.Model):
    _name = "primetech.inter.agency.transfer.line"
    _description = "Ligne de transfert inter-agences PrimeTech"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    transfer_id = fields.Many2one("primetech.inter.agency.transfer", required=True, ondelete="cascade", index=True)
    state = fields.Selection(related="transfer_id.state", store=True, index=True)
    company_id = fields.Many2one(related="transfer_id.company_id", store=True, index=True)
    source_agency_id = fields.Many2one(related="transfer_id.source_agency_id", store=True, index=True)
    destination_agency_id = fields.Many2one(related="transfer_id.destination_agency_id", store=True, index=True)
    product_id = fields.Many2one("product.product", string="Produit", required=True)
    product_uom_id = fields.Many2one("uom.uom", related="product_id.uom_id", store=True, readonly=True)
    default_code = fields.Char(related="product_id.default_code", readonly=True)
    barcode = fields.Char(related="product_id.barcode", readonly=True)
    source_location_id = fields.Many2one(related="transfer_id.source_location_id", store=True, readonly=True)
    physical_qty = fields.Float(compute="_compute_stock_quantities", readonly=True, digits="Product Unit of Measure")
    reserved_qty = fields.Float(compute="_compute_stock_quantities", readonly=True, digits="Product Unit of Measure")
    available_qty = fields.Float(string="Quantité disponible", compute="_compute_stock_quantities", readonly=True, digits="Product Unit of Measure")
    requested_qty = fields.Float(string="Quantité demandée", required=True, digits="Product Unit of Measure")
    prepared_qty = fields.Float(string="Quantité préparée", digits="Product Unit of Measure")
    shipped_qty = fields.Float(string="Quantité expédiée", digits="Product Unit of Measure")
    received_qty = fields.Float(string="Quantité reçue", digits="Product Unit of Measure")
    damaged_qty = fields.Float(digits="Product Unit of Measure")
    refused_qty = fields.Float(digits="Product Unit of Measure")
    missing_qty = fields.Float(digits="Product Unit of Measure")
    difference_qty = fields.Float(string="Écart", compute="_compute_difference", store=True, digits="Product Unit of Measure")
    lot_line_ids = fields.One2many("primetech.inter.agency.transfer.line.lot", "transfer_line_id")
    line_state = fields.Selection([("pending", "En attente"), ("prepared", "Préparée"), ("shipped", "Expédiée"), ("received", "Reçue"), ("discrepancy", "Avec écart")], default="pending")
    note = fields.Text()
    unit_cost = fields.Monetary(currency_field="currency_id")
    total_cost = fields.Monetary(compute="_compute_total_cost", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="transfer_id.currency_id")

    def _get_source_location_for_quantities(self):
        self.ensure_one()
        return self.source_location_id or self.transfer_id.source_location_id

    def _get_stock_quantities(self):
        self.ensure_one()
        source_location = self._get_source_location_for_quantities()
        if not self.product_id or not source_location:
            return {"physical_qty": 0.0, "reserved_qty": 0.0, "available_qty": 0.0}
        quants = self.env["stock.quant"].sudo().search([
            ("product_id", "=", self.product_id.id),
            ("location_id", "child_of", source_location.id),
        ])
        physical_qty = sum(quants.mapped("quantity"))
        reserved_qty = sum(quants.mapped("reserved_quantity"))
        return {
            "physical_qty": physical_qty,
            "reserved_qty": reserved_qty,
            "available_qty": physical_qty - reserved_qty,
        }

    @api.depends("product_id", "source_location_id", "transfer_id.source_location_id")
    def _compute_stock_quantities(self):
        for line in self:
            quantities = line._get_stock_quantities()
            line.physical_qty = quantities["physical_qty"]
            line.reserved_qty = quantities["reserved_qty"]
            line.available_qty = quantities["available_qty"]

    @api.onchange("product_id", "source_location_id", "transfer_id")
    def _onchange_product_stock_quantities(self):
        for line in self:
            quantities = line._get_stock_quantities()
            line.physical_qty = quantities["physical_qty"]
            line.reserved_qty = quantities["reserved_qty"]
            line.available_qty = quantities["available_qty"]
            if line.product_id and not line.requested_qty:
                line.requested_qty = 1.0

    def _refresh_stock_quantities(self):
        self.invalidate_recordset(["physical_qty", "reserved_qty", "available_qty"])
        for line in self:
            quantities = line._get_stock_quantities()
            line.physical_qty = quantities["physical_qty"]
            line.reserved_qty = quantities["reserved_qty"]
            line.available_qty = quantities["available_qty"]

    @api.depends("requested_qty", "received_qty", "damaged_qty", "refused_qty", "missing_qty")
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.requested_qty - line.received_qty - line.damaged_qty - line.refused_qty - line.missing_qty

    @api.depends("requested_qty", "unit_cost")
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.requested_qty * line.unit_cost


class PrimetechInterAgencyTransferLineLot(models.Model):
    _name = "primetech.inter.agency.transfer.line.lot"
    _description = "Lot de ligne de transfert PrimeTech"

    transfer_line_id = fields.Many2one("primetech.inter.agency.transfer.line", required=True, ondelete="cascade")
    state = fields.Selection(related="transfer_line_id.state", store=True, index=True)
    company_id = fields.Many2one(related="transfer_line_id.company_id", store=True, index=True)
    source_agency_id = fields.Many2one(related="transfer_line_id.source_agency_id", store=True, index=True)
    destination_agency_id = fields.Many2one(related="transfer_line_id.destination_agency_id", store=True, index=True)
    lot_id = fields.Many2one("stock.lot", required=True)
    expiration_date = fields.Datetime(related="lot_id.expiration_date", readonly=True)
    available_qty = fields.Float(readonly=True, digits="Product Unit of Measure")
    prepared_qty = fields.Float(digits="Product Unit of Measure")
    shipped_qty = fields.Float(digits="Product Unit of Measure")
    received_qty = fields.Float(digits="Product Unit of Measure")
    difference_qty = fields.Float(compute="_compute_difference", store=True, digits="Product Unit of Measure")

    @api.depends("shipped_qty", "received_qty")
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.shipped_qty - line.received_qty
