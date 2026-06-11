from odoo import models


class SalesPeriodicXlsx(
    models.AbstractModel
):

    _name = (
        "report.primetech_reporting_center.sales_periodic_xlsx"
    )

    _inherit = (
        "report.report_xlsx.abstract"
    )

    _description = (
        "Rapport Périodique des Ventes XLSX"
    )

    def generate_xlsx_report(

        self,

        workbook,

        data,

        wizard,

    ):

        report_data = self.env[
            "primetech.sales.periodic.report"
        ].get_report_data(

            date_from=wizard.date_from,

            date_to=wizard.date_to,

            company_id=wizard.company_id.id,

            user_id=wizard.user_id.id
            if wizard.user_id
            else False,

            partner_id=wizard.partner_id.id
            if wizard.partner_id
            else False,

            state_filter=wizard.state_filter,

        )

        sheet = workbook.add_worksheet(
            "Ventes"
        )

        title = workbook.add_format({

            "bold": True,

            "font_size": 14,

            "align": "center",

        })

        header = workbook.add_format({

            "bold": True,

            "border": 1,

        })

        amount = workbook.add_format({

            "num_format":
                "#,##0.00",

            "border": 1,

        })

        normal = workbook.add_format({

            "border": 1,

        })

        row = 0

        sheet.merge_range(

            row,
            0,
            row,
            7,

            "RAPPORT PERIODIQUE DES VENTES",

            title,

        )

        row += 2

        sheet.write(
            row,
            0,
            "Date Début"
        )

        sheet.write(
            row,
            1,
            str(
                wizard.date_from
            )
        )

        row += 1

        sheet.write(
            row,
            0,
            "Date Fin"
        )

        sheet.write(
            row,
            1,
            str(
                wizard.date_to
            )
        )

        row += 3

        headers = [

            "Facture",

            "Date",

            "Client",

            "Commercial",

            "Produit",

            "Qté",

            "HT",

            "TTC",

        ]

        for col, value in enumerate(
            headers
        ):

            sheet.write(

                row,

                col,

                value,

                header,

            )

        row += 1

        for line in report_data[
            "sales_lines"
        ]:

            sheet.write(
                row,
                0,
                line["invoice"],
                normal,
            )

            sheet.write(
                row,
                1,
                str(
                    line["date"]
                ),
                normal,
            )

            sheet.write(
                row,
                2,
                line["customer"],
                normal,
            )

            sheet.write(
                row,
                3,
                line["seller"],
                normal,
            )

            sheet.write(
                row,
                4,
                line["product"],
                normal,
            )

            sheet.write(
                row,
                5,
                line["qty"],
                normal,
            )

            sheet.write(
                row,
                6,
                line["ht"],
                amount,
            )

            sheet.write(
                row,
                7,
                line["ttc"],
                amount,
            )

            row += 1

        sheet.set_column(
            0,
            7,
            20
        )