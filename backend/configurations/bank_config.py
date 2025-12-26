BANK_MAPPINGS = {
    "hdfc": {
        "date": "Txn Date",
        "description": "Narration",
        "debit": "Withdrawal Amt.",
        "credit": "Deposit Amt.",
        "date_format": "%d/%m/%y",
    },
    "ipko": {
        "date": "Data operacji",
        "description": "Tytuł",
        "amount": "Kwota",
        "currency": "Waluta",
        "date_format": "%Y-%m-%d",
    },
    "millennium": {
        "date": "Transaction date",
        "description": "Description",
        "debit": "Debits",
        "credit": "Credits",
        "date_format": "%Y-%m-%d",
    },
    "alior": {
        "date": "Data transakcji",
        "description": "Opis transakcji",
        "amount": "Kwota",
        "currency": "Waluta",
        "date_format": "%Y-%m-%d",
    },
    "axis": {
        "date": "Transaction Date",
        "description": "Particulars",
        "debit": "Debit",
        "credit": "Credit",
        "date_format": "%d-%m-%Y",
    },
    "revolut": {
        "date": "Started Date",
        "description": "Description",
        "amount": "Amount",
        "fee": "Fee",
        "currency": "Currency",
        "date_format": "%Y-%m-%d %H:%M:%S",
    },
    "SBI": {
        "date": "Started Date",
        "description": "Description",
        "amount": "Amount",
        "fee": "Fee",
        "currency": "Currency",
        "date_format": "%Y-%m-%d %H:%M:%S",
    },
}

# Category IDs based on user mapping:
# 1: Administrative Expenses, 2: Bank Fees, 3: Bills, 4: Clothing, 5: Entertainment,
# 6: Food, 7: Fuel, 8: Gift, 9: Health, 10: Home, 11: Loan Repayment,
# 12: Misc, 13: Money Transfer, 14: Rent, 15: School Fees, 16: Shopping,
# 17: Transport, 18: New Home, 19: International Travel

CATEGORY_RULES = {
    1: [],
    2: [],
    3: ["flex.orange.pl", "Administration", "mojeuslugi.play.pl"],
    4: ["DEALZ", "KIK", "TEDI", "vinted"],
    5: [],
    6: ["KOKU Sushi"],
    7: ["SHELL"],
    8: [],
    9: ["SUPER-PHARM"],
    10: ["TransferWise", "Wise Europe SA", "P17588790"],
    11: ["Loan repayment", ],
    12: [],  # Misc default
    13: [],
    14: ["RENT", "storage box"],
    15: ["GDANSK TAEKWON-DO CLUB"],
    16: ["LITTLE INDIA", "India Bazaar", "AUCHAN", "LIDL", "eLeclerc", "olx", "allegro.pl", "temu", "DOUGLAS",
         "MARKET OBI"],
    17: ["systemfala", "www.jestemzgdanska.pl", "UBER", "BOLT.EU", "jakdojade"],
    18: [],
    19: [],
}

INCOME_SOURCE_RULES = {
    1: ["Wynagrodzenie", "WIPRO IT SERVICES", "EPAM SYSTEMS POLAND"],
    2: [],
    3: [],
    4: ["dividend"],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
    11: [],
    12: ["zus"],
    13: ["tax", "refund", "return"],
    14: [],  # Misc default
}

DEFAULT_INCOME_SOURCE_ID = 14
DEFAULT_CATEGORY_ID = 12
