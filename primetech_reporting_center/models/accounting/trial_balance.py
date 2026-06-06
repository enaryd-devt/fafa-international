from collections import defaultdict

from odoo import api, fields, models

OHADA_CLASSES = {

    "1": "COMPTES DE RESSOURCES DURABLES",

    "2": "COMPTES D'ACTIF IMMOBILISÉ",

    "3": "COMPTES DE STOCKS",

    "4": "COMPTES DE TIERS",

    "5": "COMPTES DE TRÉSORERIE",

    "6": "COMPTES DE CHARGES",

    "7": "COMPTES DE PRODUITS",

    "8": "AUTRES CHARGES ET AUTRES PRODUITS",

    "9": "COMPTES ANALYTIQUES",

}
    
OHADA_LEVEL2 = {

    # =========================
    # CLASSE 1
    # RESSOURCES DURABLES
    # =========================

    "10": "CAPITAL",
    "11": "RÉSERVES",
    "12": "REPORT À NOUVEAU",
    "13": "RÉSULTAT NET DE L'EXERCICE",
    "14": "SUBVENTIONS D'INVESTISSEMENT",
    "15": "PROVISIONS RÉGLEMENTÉES ET FONDS ASSIMILÉS",
    "16": "EMPRUNTS ET DETTES FINANCIÈRES",
    "17": "DETTES DE CRÉDIT-BAIL ET CONTRATS ASSIMILÉS",
    "18": "DETTES LIÉES À DES PARTICIPATIONS",
    "19": "PROVISIONS FINANCIÈRES POUR RISQUES ET CHARGES",

    # =========================
    # CLASSE 2
    # ACTIF IMMOBILISÉ
    # =========================

    "20": "CHARGES IMMOBILISÉES",
    "21": "IMMOBILISATIONS INCORPORELLES",
    "22": "TERRAINS",
    "23": "BÂTIMENTS, INSTALLATIONS TECHNIQUES ET AGENCEMENTS",
    "24": "MATÉRIEL",
    "25": "AVANCES ET ACOMPTES VERSÉS SUR IMMOBILISATIONS",
    "26": "TITRES DE PARTICIPATION",
    "27": "AUTRES IMMOBILISATIONS FINANCIÈRES",
    "28": "AMORTISSEMENTS",
    "29": "DÉPRÉCIATIONS DES IMMOBILISATIONS",

    # =========================
    # CLASSE 3
    # STOCKS
    # =========================

    "31": "MARCHANDISES",
    "32": "MATIÈRES PREMIÈRES ET FOURNITURES LIÉES",
    "33": "AUTRES APPROVISIONNEMENTS",
    "34": "PRODUITS EN COURS",
    "35": "SERVICES EN COURS",
    "36": "PRODUITS FINIS",
    "37": "PRODUITS INTERMÉDIAIRES ET RÉSIDUELS",
    "38": "STOCKS EN COURS DE ROUTE",
    "39": "DÉPRÉCIATIONS DES STOCKS",

    # =========================
    # CLASSE 4
    # TIERS
    # =========================

    "40": "FOURNISSEURS ET COMPTES RATTACHÉS",
    "41": "CLIENTS ET COMPTES RATTACHÉS",
    "42": "PERSONNEL",
    "43": "ORGANISMES SOCIAUX",
    "44": "ÉTAT ET COLLECTIVITÉS PUBLIQUES",
    "45": "ORGANISMES INTERNATIONAUX",
    "46": "ASSOCIÉS ET GROUPE",
    "47": "DÉBITEURS ET CRÉDITEURS DIVERS",
    "48": "CRÉANCES ET DETTES HORS ACTIVITÉS ORDINAIRES",
    "49": "DÉPRÉCIATIONS ET RISQUES PROVISIONNÉS",

    # =========================
    # CLASSE 5
    # TRÉSORERIE
    # =========================

    "50": "TITRES DE PLACEMENT",
    "51": "VALEURS À ENCAISSER",
    "52": "BANQUES",
    "53": "ÉTABLISSEMENTS FINANCIERS",
    "54": "INSTRUMENTS DE TRÉSORERIE",
    "55": "INSTRUMENTS FINANCIERS À TERME",
    "56": "BANQUES CRÉDITRICES",
    "57": "CAISSE",
    "58": "RÉGIES D'AVANCES ET ACCRÉDITIFS",
    "59": "DÉPRÉCIATIONS ET RISQUES PROVISIONNÉS",

    # =========================
    # CLASSE 6
    # CHARGES
    # =========================

    "60": "ACHATS ET VARIATIONS DE STOCKS",
    "61": "TRANSPORTS",
    "62": "SERVICES EXTÉRIEURS A",
    "63": "SERVICES EXTÉRIEURS B",
    "64": "IMPÔTS ET TAXES",
    "65": "AUTRES CHARGES",
    "66": "CHARGES DE PERSONNEL",
    "67": "FRAIS FINANCIERS ET CHARGES ASSIMILÉES",
    "68": "DOTATIONS AUX AMORTISSEMENTS ET PROVISIONS",
    "69": "IMPÔTS SUR LES RÉSULTATS",

    # =========================
    # CLASSE 7
    # PRODUITS
    # =========================

    "70": "VENTES",
    "71": "SUBVENTIONS D'EXPLOITATION",
    "72": "PRODUCTION IMMOBILISÉE",
    "73": "VARIATION DES STOCKS DE BIENS ET SERVICES PRODUITS",
    "74": "PRODUCTION STOCKÉE",
    "75": "AUTRES PRODUITS",
    "76": "TRANSFERTS DE CHARGES",
    "77": "REVENUS FINANCIERS ET PRODUITS ASSIMILÉS",
    "78": "REPRISES DE PROVISIONS",
    "79": "TRANSFERTS DE CHARGES ET AUTRES REPRISES",

    # =========================
    # CLASSE 8
    # HAO
    # =========================

    "81": "VALEURS COMPTABLES DES CESSIONS",
    "82": "PRODUITS DES CESSIONS",
    "83": "CHARGES HORS ACTIVITÉS ORDINAIRES",
    "84": "PRODUITS HORS ACTIVITÉS ORDINAIRES",
    "85": "DOTATIONS HAO",
    "86": "REPRISES HAO",
    "87": "PARTICIPATION DES TRAVAILLEURS",
    "88": "SUBVENTIONS D'ÉQUILIBRE",
    "89": "IMPÔTS SUR LE RÉSULTAT HAO",

}
OHADA_LEVEL3 = {

    # =====================================
    # CLASSE 1
    # =====================================

    "101": "CAPITAL SOCIAL",
    "102": "CAPITAL PAR DOTATION",
    "103": "CAPITAL PERSONNEL",
    "104": "ACTIONNAIRES, CAPITAL SOUSCRIT NON APPELÉ",
    "105": "ÉCARTS DE RÉÉVALUATION",

    "111": "RÉSERVE LÉGALE",
    "112": "RÉSERVES STATUTAIRES",
    "113": "RÉSERVES FACULTATIVES",
    "118": "AUTRES RÉSERVES",

    "121": "REPORT À NOUVEAU CRÉDITEUR",
    "129": "REPORT À NOUVEAU DÉBITEUR",

    "131": "RÉSULTAT NET : BÉNÉFICE",
    "139": "RÉSULTAT NET : PERTE",

    "141": "SUBVENTIONS D'INVESTISSEMENT",

    "151": "PROVISIONS POUR RECONSTITUTION DE GISEMENT",
    "152": "PROVISIONS POUR INVESTISSEMENT",

    "161": "EMPRUNTS OBLIGATAIRES",
    "162": "EMPRUNTS AUPRÈS DES ÉTABLISSEMENTS DE CRÉDIT",
    "166": "DÉPÔTS ET CAUTIONNEMENTS REÇUS",

    # =====================================
    # CLASSE 2
    # =====================================

    "201": "FRAIS D'ÉTABLISSEMENT",
    "202": "CHARGES À RÉPARTIR",
    "203": "PRIMES DE REMBOURSEMENT",

    "211": "BREVETS, LICENCES",
    "212": "LOGICIELS",
    "213": "FONDS COMMERCIAL",

    "221": "TERRAINS AGRICOLES",
    "222": "TERRAINS BÂTIS",

    "231": "BÂTIMENTS INDUSTRIELS",
    "232": "BÂTIMENTS ADMINISTRATIFS",

    "241": "MATÉRIEL ET OUTILLAGE",
    "242": "MATÉRIEL DE TRANSPORT",
    "243": "MATÉRIEL DE BUREAU",
    "244": "MOBILIER",
    "245": "MATÉRIEL INFORMATIQUE",

    "261": "TITRES DE PARTICIPATION",

    "271": "PRÊTS",
    "273": "DÉPÔTS ET CAUTIONNEMENTS",

    # =====================================
    # CLASSE 3
    # =====================================

    "311": "MARCHANDISES A",
    "312": "MARCHANDISES B",

    "321": "MATIÈRES PREMIÈRES",
    "322": "FOURNITURES LIÉES",

    "331": "MATIÈRES CONSOMMABLES",
    "332": "FOURNITURES D'ATELIER",

    "361": "PRODUITS FINIS",

    # =====================================
    # CLASSE 4
    # =====================================

    "401": "FOURNISSEURS",
    "402": "FOURNISSEURS D'IMMOBILISATIONS",
    "408": "FOURNISSEURS FACTURES NON PARVENUES",

    "411": "CLIENTS",
    "412": "CLIENTS EFFETS À RECEVOIR",
    "418": "CLIENTS PRODUITS À RECEVOIR",

    "421": "PERSONNEL AVANCES ET ACOMPTES",
    "422": "RÉMUNÉRATIONS DUES",

    "431": "SÉCURITÉ SOCIALE",

    "441": "ÉTAT IMPÔTS ET TAXES",
    "442": "ÉTAT TVA",

    "461": "ASSOCIÉS",

    "471": "DÉBITEURS DIVERS",
    "472": "CRÉDITEURS DIVERS",

    # =====================================
    # CLASSE 5
    # =====================================

    "521": "BANQUES LOCALES",
    "522": "BANQUES ÉTRANGÈRES",

    "531": "ÉTABLISSEMENTS FINANCIERS",

    "571": "CAISSE SIÈGE",
    "572": "CAISSES SUCCURSALES",

    # =====================================
    # CLASSE 6
    # =====================================

    "601": "ACHATS DE MARCHANDISES",
    "602": "ACHATS DE MATIÈRES PREMIÈRES",
    "603": "VARIATION DES STOCKS",

    "611": "TRANSPORTS SUR ACHATS",
    "612": "TRANSPORTS SUR VENTES",

    "621": "SOUS-TRAITANCE",
    "622": "LOCATIONS",
    "623": "ENTRETIEN ET RÉPARATIONS",
    "624": "PRIMES D'ASSURANCE",

    "641": "IMPÔTS DIRECTS",
    "646": "DROITS DE DOUANE",

    "661": "SALAIRES ET TRAITEMENTS",
    "664": "CHARGES SOCIALES",

    "671": "INTÉRÊTS DES EMPRUNTS",

    "681": "DOTATIONS AUX AMORTISSEMENTS",

    # =====================================
    # CLASSE 7
    # =====================================

    "701": "VENTES DE MARCHANDISES",
    "702": "VENTES DE PRODUITS FINIS",
    "706": "PRESTATIONS DE SERVICES",

    "711": "SUBVENTIONS D'EXPLOITATION",

    "751": "PRODUITS DIVERS",

    "771": "REVENUS DES PARTICIPATIONS",
    "772": "REVENUS DES PRÊTS",

    "781": "REPRISES D'AMORTISSEMENTS",

    # =====================================
    # CLASSE 8
    # =====================================

    "831": "CHARGES HAO",

    "841": "PRODUITS HAO",

    "871": "PARTICIPATION DES TRAVAILLEURS",

}

from collections import defaultdict

from odoo import api, models


class PrimetechTrialBalance(models.AbstractModel):

    _name = "primetech.trial.balance"

    _description = "Primetech Trial Balance"

    def _get_level(self, code):

        if len(code) == 1:
            return 1

        if len(code) == 2:
            return 2

        if len(code) == 3:
            return 3

        return 4

    def _get_name(
        self,
        code,
        account=None,
    ):

        if len(code) == 1:

            return OHADA_CLASSES.get(
                code,
                code
            )

        if len(code) == 2:

            return OHADA_LEVEL2.get(
                code,
                code
            )

        if len(code) == 3:

            return OHADA_LEVEL3.get(
                code,
                code
            )

        return account.name if account else code

    @api.model
    def get_trial_balance(
        self,
        date_from=False,
        date_to=False,
    ):

        Account = self.env[
            "account.account"
        ]

        MoveLine = self.env[
            "account.move.line"
        ]

        balances = defaultdict(
            lambda: {

                "code": "",

                "name": "",

                "level": 0,

                "opening_debit": 0.0,

                "opening_credit": 0.0,

                "period_debit": 0.0,

                "period_credit": 0.0,

                "closing_debit": 0.0,

                "closing_credit": 0.0,

            }
        )

        accounts = Account.search(
            [],
            order="code"
        )

        for account in accounts:

            code = account.code or ""

            prefixes = [

                code[:1],

                code[:2],

                code[:3],

                code,

            ]

            opening_domain = [

                (
                    "account_id",
                    "=",
                    account.id
                ),

                (
                    "parent_state",
                    "=",
                    "posted"
                )

            ]

            if date_from:

                opening_domain.append(

                    (
                        "date",
                        "<",
                        date_from
                    )

                )

            opening_lines = MoveLine.search(
                opening_domain
            )

            period_domain = [

                (
                    "account_id",
                    "=",
                    account.id
                ),

                (
                    "parent_state",
                    "=",
                    "posted"
                )

            ]

            if date_from:

                period_domain.append(

                    (
                        "date",
                        ">=",
                        date_from
                    )

                )

            if date_to:

                period_domain.append(

                    (
                        "date",
                        "<=",
                        date_to
                    )

                )

            period_lines = MoveLine.search(
                period_domain
            )

            opening_debit = sum(
                opening_lines.mapped(
                    "debit"
                )
            )

            opening_credit = sum(
                opening_lines.mapped(
                    "credit"
                )
            )

            period_debit = sum(
                period_lines.mapped(
                    "debit"
                )
            )

            period_credit = sum(
                period_lines.mapped(
                    "credit"
                )
            )

            closing_debit = (
                opening_debit
                +
                period_debit
            )

            closing_credit = (
                opening_credit
                +
                period_credit
            )

            for prefix in prefixes:

                line = balances[
                    prefix
                ]

                line["code"] = prefix

                line["name"] = self._get_name(
                    prefix,
                    account
                )

                line["level"] = self._get_level(
                    prefix
                )

                line["opening_debit"] += (
                    opening_debit
                )

                line["opening_credit"] += (
                    opening_credit
                )

                line["period_debit"] += (
                    period_debit
                )

                line["period_credit"] += (
                    period_credit
                )

                line["closing_debit"] += (
                    closing_debit
                )

                line["closing_credit"] += (
                    closing_credit
                )

        result = list(
            balances.values()
        )

        result.sort(

            key=lambda x: (

                x["code"],

                x["level"]

            )

        )

        total_opening_debit = sum(

            line["opening_debit"]

            for line in result

            if line["level"] == 4

        )

        total_opening_credit = sum(

            line["opening_credit"]

            for line in result

            if line["level"] == 4

        )

        total_period_debit = sum(

            line["period_debit"]

            for line in result

            if line["level"] == 4

        )

        total_period_credit = sum(

            line["period_credit"]

            for line in result

            if line["level"] == 4

        )

        total_closing_debit = sum(

            line["closing_debit"]

            for line in result

            if line["level"] == 4

        )

        total_closing_credit = sum(

            line["closing_credit"]

            for line in result

            if line["level"] == 4

        )

        return {

            "lines": result,

            "totals_balance": {

                "opening_debit":
                    total_opening_debit,

                "opening_credit":
                    total_opening_credit,

                "period_debit":
                    total_period_debit,

                "period_credit":
                    total_period_credit,

                "closing_debit":
                    total_closing_debit,

                "closing_credit":
                    total_closing_credit,

            },

        }