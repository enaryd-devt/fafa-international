# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models


class SalesPeriodicXlsx(models.AbstractModel):

    _name = "report.primetech_reporting_center.sales_periodic_xlsx"

    _inherit = "report.report_xlsx.abstract"

    _description = "Rapport XLSX Périodique des Ventes"

    def generate_xlsx_report(
        self,
        workbook,
        data,
        wizard,
    ):

        # ============================================================
        # FEUILLE
        # ============================================================

        sheet = workbook.add_worksheet(
            "Rapport des ventes"
        )

        sheet.freeze_panes(9, 0)

        sheet.set_zoom(90)

        # ============================================================
        # FORMATS
        # ============================================================

        title = workbook.add_format({

            "bold": True,

            "font_size": 18,

            "align": "center",

            "valign": "vcenter",

            "font_color": "#FFFFFF",

            "bg_color": "#1F4E79",

        })

        subtitle = workbook.add_format({

            "bold": True,

            "font_size": 11,

            "font_color": "#1F4E79",

        })

        section = workbook.add_format({

            "bold": True,

            "font_size": 13,

            "font_color": "#FFFFFF",

            "bg_color": "#1F4E79",

            "border": 1,

            "align": "center",

            "valign": "vcenter",

        })

        header = workbook.add_format({

            "bold": True,

            "font_color": "#FFFFFF",

            "bg_color": "#4472C4",

            "border": 1,

            "align": "center",

            "valign": "vcenter",

        })

        cell = workbook.add_format({

            "border": 1,

            "valign": "top",

        })

        center = workbook.add_format({

            "border": 1,

            "align": "center",

            "valign": "vcenter",

        })

        right = workbook.add_format({

            "border": 1,

            "align": "right",

            "valign": "vcenter",

        })

        money = workbook.add_format({

            "border": 1,

            "align": "right",

            "num_format": "#,##0.00",

        })

        integer = workbook.add_format({

            "border": 1,

            "align": "center",

            "num_format": "#,##0",

        })

        decimal = workbook.add_format({

            "border": 1,

            "align": "center",

            "num_format": "#,##0.00",

        })

        total = workbook.add_format({

            "bold": True,

            "font_color": "#FFFFFF",

            "bg_color": "#1F4E79",

            "border": 1,

            "num_format": "#,##0.00",

        })

        total_center = workbook.add_format({

            "bold": True,

            "font_color": "#FFFFFF",

            "bg_color": "#1F4E79",

            "border": 1,

            "align": "center",

        })

        # ============================================================
        # DONNEES
        # ============================================================

        report_data = self.env[
            "primetech.sales.periodic.report"
        ].get_report_data(

            date_from=wizard.date_from,

            date_to=wizard.date_to,

            company_id=wizard.company_id.id,

            user_id=(
                wizard.user_id.id
                if wizard.user_id
                else False
            ),

            partner_id=(
                wizard.partner_id.id
                if wizard.partner_id
                else False
            ),

            state_filter=wizard.state_filter,

        )

        summary = report_data.get("summary", {})

        sales_lines = report_data.get(
            "sales_lines",
            [],
        )

        seller_summary = report_data.get(
            "seller_summary",
            [],
        )

        customer_summary = report_data.get(
            "customer_summary",
            [],
        )

        product_summary = report_data.get(
            "product_summary",
            [],
        )

        warehouse_summary = report_data.get(
            "warehouse_summary",
            [],
        )

        top_customers = report_data.get(
            "top_customers",
            [],
        )

        top_products = report_data.get(
            "top_products",
            [],
        )

        top_salespersons = report_data.get(
            "top_salespersons",
            [],
        )

        top_warehouses = report_data.get(
            "top_warehouses",
            [],
        )

        # ============================================================
        # ENTETE
        # ============================================================

        row = 0

        sheet.merge_range(

            row,

            0,

            row,

            10,

            "RAPPORT PERIODIQUE DES VENTES",

            title,

        )

        row += 2

        sheet.write(

            row,

            0,

            "Société",

            subtitle,

        )

        sheet.write(

            row,

            1,

            wizard.company_id.name,

        )

        sheet.write(

            row,

            4,

            "Période",

            subtitle,

        )

        sheet.write(

            row,

            5,

            f"{wizard.date_from} au {wizard.date_to}",

        )

        sheet.write(

            row,

            8,

            "Généré le",

            subtitle,

        )

        sheet.write(

            row,

            9,

            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            ),

        )

        row += 3
                # ============================================================
        # RÉSUMÉ GÉNÉRAL
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            10,
            "RÉSUMÉ GÉNÉRAL",
            section,
        )

        row += 2

        sheet.write(row, 0, "Nombre de ventes", cell)
        sheet.write(
            row,
            1,
            summary.get(
                "sale_count",
                summary.get("invoice_count", 0),
            ),
            integer,
        )

        sheet.write(row, 3, "Nombre de clients", cell)
        sheet.write(
            row,
            4,
            summary.get("customer_count", 0),
            integer,
        )

        sheet.write(row, 6, "Nombre de commerciaux", cell)
        sheet.write(
            row,
            7,
            summary.get("seller_count", 0),
            integer,
        )

        sheet.write(row, 9, "Nombre de magasins", cell)
        sheet.write(
            row,
            10,
            summary.get("warehouse_count", 0),
            integer,
        )

        row += 1

        sheet.write(row, 0, "Quantité vendue", cell)
        sheet.write(
            row,
            1,
            summary.get("qty_sold", 0),
            decimal,
        )

        sheet.write(row, 3, "CA HT", cell)
        sheet.write(
            row,
            4,
            summary.get("turnover_ht", 0),
            money,
        )

        sheet.write(row, 6, "CA TTC", cell)
        sheet.write(
            row,
            7,
            summary.get("turnover_ttc", 0),
            money,
        )

        sheet.write(row, 9, "Ticket moyen", cell)
        sheet.write(
            row,
            10,
            summary.get("average_ticket", 0),
            money,
        )

        row += 3

        # ============================================================
        # INDICATEURS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            10,
            "INDICATEURS",
            section,
        )

        row += 2

        sheet.write(row, 0, "Plus gros client", cell)

        sheet.write(
            row,
            1,
            top_customers[0]["customer"]
            if top_customers
            else "-",
            cell,
        )

        sheet.write(row, 3, "Meilleur commercial", cell)

        sheet.write(
            row,
            4,
            top_salespersons[0]["seller"]
            if top_salespersons
            else "-",
            cell,
        )

        sheet.write(row, 6, "Produit N°1", cell)

        sheet.write(
            row,
            7,
            top_products[0]["product"]
            if top_products
            else "-",
            cell,
        )

        sheet.write(row, 9, "Magasin N°1", cell)

        sheet.write(
            row,
            10,
            top_warehouses[0]["warehouse"]
            if top_warehouses
            else "-",
            cell,
        )

        row += 3
                # ============================================================
        # DETAIL DES VENTES
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            11,
            "DETAIL DES VENTES",
            section,
        )

        row += 2

        headers = [

            "Document",

            "Date",

            "Client",

            "Commercial",

            "Magasin",

            "Produit",

            "Qté",

            "Qté livrée",

            "Qté facturée",

            "PU HT",

            "Total HT",

            "Total TTC",

        ]

        for col, value in enumerate(headers):

            sheet.write(
                row,
                col,
                value,
                header,
            )

        row += 1

        start_detail = row

        for line in sales_lines:

            sheet.write(
                row,
                0,
                line.get("invoice")
                or line.get("reference")
                or line.get("order")
                or "-",
                cell,
            )

            sheet.write(
                row,
                1,
                str(line.get("date") or ""),
                center,
            )

            sheet.write(
                row,
                2,
                line.get("customer", ""),
                cell,
            )

            sheet.write(
                row,
                3,
                line.get("seller", ""),
                cell,
            )

            sheet.write(
                row,
                4,
                line.get("warehouse", ""),
                cell,
            )

            sheet.write(
                row,
                5,
                line.get("product", ""),
                cell,
            )

            sheet.write(
                row,
                6,
                line.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                7,
                line.get("qty_delivered", 0),
                decimal,
            )

            sheet.write(
                row,
                8,
                line.get("qty_invoiced", 0),
                decimal,
            )

            sheet.write(
                row,
                9,
                line.get("unit_price", 0),
                money,
            )

            sheet.write(
                row,
                10,
                line.get("ht", 0),
                money,
            )

            sheet.write(
                row,
                11,
                line.get("ttc", 0),
                money,
            )

            row += 1

        # ============================================================
        # TOTAL DETAIL
        # ============================================================

        sheet.write(
            row,
            0,
            "TOTAL",
            total_center,
        )

        sheet.merge_range(
            row,
            1,
            row,
            5,
            "",
            total,
        )

        sheet.write_formula(
            row,
            6,
            f"=SUM(G{start_detail+1}:G{row})",
            total,
        )

        sheet.write_formula(
            row,
            7,
            f"=SUM(H{start_detail+1}:H{row})",
            total,
        )

        sheet.write_formula(
            row,
            8,
            f"=SUM(I{start_detail+1}:I{row})",
            total,
        )

        sheet.write_formula(
            row,
            9,
            "",
            total,
        )

        sheet.write_formula(
            row,
            10,
            f"=SUM(K{start_detail+1}:K{row})",
            total,
        )

        sheet.write_formula(
            row,
            11,
            f"=SUM(L{start_detail+1}:L{row})",
            total,
        )

        row += 3
                # ============================================================
        # SYNTHESE PAR COMMERCIAL
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "SYNTHESE PAR COMMERCIAL",
            section,
        )

        row += 1

        headers = [
            "Commercial",
            "Qté",
            "CA HT",
            "CA TTC",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        total_ht = summary.get("turnover_ht", 0)

        for seller in seller_summary:

            sheet.write(
                row,
                0,
                seller.get("seller", ""),
                cell,
            )

            sheet.write(
                row,
                1,
                seller.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                2,
                seller.get("ht", 0),
                money,
            )

            sheet.write(
                row,
                3,
                seller.get("ttc", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    seller.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # SYNTHESE PAR CLIENT
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            3,
            "SYNTHESE PAR CLIENT",
            section,
        )

        row += 1

        headers = [
            "Client",
            "CA HT",
            "CA TTC",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for customer in customer_summary:

            sheet.write(
                row,
                0,
                customer.get("customer", ""),
                cell,
            )

            sheet.write(
                row,
                1,
                customer.get("ht", 0),
                money,
            )

            sheet.write(
                row,
                2,
                customer.get("ttc", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    customer.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                3,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # SYNTHESE PAR PRODUIT
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            3,
            "SYNTHESE PAR PRODUIT",
            section,
        )

        row += 1

        headers = [
            "Produit",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for product in product_summary:

            sheet.write(
                row,
                0,
                product.get("product", ""),
                cell,
            )

            sheet.write(
                row,
                1,
                product.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                2,
                product.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    product.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                3,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # SYNTHESE PAR MAGASIN
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            3,
            "SYNTHESE PAR MAGASIN",
            section,
        )

        row += 1

        headers = [
            "Magasin",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for warehouse in warehouse_summary:

            sheet.write(
                row,
                0,
                warehouse.get("warehouse", ""),
                cell,
            )

            sheet.write(
                row,
                1,
                warehouse.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                2,
                warehouse.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    warehouse.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                3,
                percent,
                decimal,
            )

            row += 2
                    # ============================================================
        # TOP 10 CLIENTS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            3,
            "TOP 10 CLIENTS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Client",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, customer in enumerate(top_customers, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                customer.get("customer", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                customer.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    customer.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                3,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP 10 PRODUITS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP 10 PRODUITS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Produit",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, product in enumerate(top_products, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                product.get("product", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                product.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                product.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    product.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP 10 COMMERCIAUX
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP 10 COMMERCIAUX",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Commercial",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, seller in enumerate(top_salespersons, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                seller.get("seller", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                seller.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                seller.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    seller.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP MAGASINS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP MAGASINS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Magasin",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, warehouse in enumerate(top_warehouses, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                warehouse.get("warehouse", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                warehouse.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                warehouse.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    warehouse.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 2
                    # ============================================================
        # TOP 10 CLIENTS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            3,
            "TOP 10 CLIENTS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Client",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, customer in enumerate(top_customers, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                customer.get("customer", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                customer.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    customer.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                3,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP 10 PRODUITS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP 10 PRODUITS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Produit",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, product in enumerate(top_products, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                product.get("product", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                product.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                product.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    product.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP 10 COMMERCIAUX
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP 10 COMMERCIAUX",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Commercial",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, seller in enumerate(top_salespersons, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                seller.get("seller", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                seller.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                seller.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    seller.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 1

        row += 2

        # ============================================================
        # TOP MAGASINS
        # ============================================================

        sheet.merge_range(
            row,
            0,
            row,
            4,
            "TOP MAGASINS",
            section,
        )

        row += 1

        headers = [
            "Rang",
            "Magasin",
            "Qté",
            "CA HT",
            "%",
        ]

        for col, h in enumerate(headers):
            sheet.write(row, col, h, header)

        row += 1

        for i, warehouse in enumerate(top_warehouses, start=1):

            sheet.write(row, 0, i, integer)

            sheet.write(
                row,
                1,
                warehouse.get("warehouse", ""),
                cell,
            )

            sheet.write(
                row,
                2,
                warehouse.get("qty", 0),
                decimal,
            )

            sheet.write(
                row,
                3,
                warehouse.get("ht", 0),
                money,
            )

            percent = 0

            if total_ht:
                percent = (
                    warehouse.get("ht", 0)
                    * 100
                    / total_ht
                )

            sheet.write(
                row,
                4,
                percent,
                decimal,
            )

            row += 2