import csv
import io
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from backend.configurations.bank_config import (
    BANK_MAPPINGS,
    CATEGORY_RULES,
    DEFAULT_CATEGORY_ID,
    INCOME_SOURCE_RULES,
    DEFAULT_INCOME_SOURCE_ID,
)
from backend.schemas.expense_schema import ExpenseCreate
from backend.schemas.income_schema import IncomeCreate
from backend.services.expense_services import create_expense
from backend.services.income_services import create_income

logger = logging.getLogger(__name__)


def normalize_headers(decoded_file: str, delimiter: str):
    """
    Normalize empty/duplicate headers and return headers + data lines.
    """
    lines = decoded_file.splitlines()
    header_line = lines[0]

    raw_headers = next(csv.reader([header_line], delimiter=delimiter))

    headers = []
    seen = {}
    extra_index = 1

    for h in raw_headers:
        name = h.strip()

        if not name:
            name = f"__extra_{extra_index}"
            extra_index += 1

        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1

        headers.append(name)

    # Return headers + remaining CSV content (WITHOUT header line)
    remaining_csv = "\n".join(lines[1:])
    return headers, remaining_csv


def parse_date(date_str: str, fmt: str) -> datetime:
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        # Fallback for common variations if needed
        return datetime.now()


def extract_extra_columns(row: dict) -> str:
    """
    Collects values from generated __extra_* columns.
    """
    extras = [
        v.strip()
        for k, v in row.items()
        if k.startswith("__extra_") and v and v.strip()
    ]
    return " ".join(extras)


def build_full_description(row: dict, primary_desc_col: str | None) -> str:
    """
    Builds a single searchable description string from:
    - main description column
    - all __extra_* columns
    """
    parts = []

    if primary_desc_col:
        main_desc = row.get(primary_desc_col)
        if main_desc:
            parts.append(main_desc.strip())

    for key, value in row.items():
        if (key.startswith("__extra_") | key.startswith("Benefeciary")) and value and value.strip():
            parts.append(value.strip())

    return " | ".join(parts)


def determine_category(description: str) -> int:
    description = description.lower()
    print(f"\n[DEBUG] Categorizing: '{description}'")
    for cat_id, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in description:
                print(f"[DEBUG]   Matched keyword '{keyword}' -> Category ID {cat_id}")
                return cat_id
    print(f"[DEBUG]   No match found. Using Default Category ID {DEFAULT_CATEGORY_ID}")
    return DEFAULT_CATEGORY_ID


def determine_income_source(description: str) -> int:
    description = description.lower()
    print(f"\n[DEBUG] Determining Income Source: '{description}'")
    for source_id, keywords in INCOME_SOURCE_RULES.items():
        for keyword in keywords:
            if keyword.lower() in description:
                print(f"[DEBUG]   Matched keyword '{keyword}' -> Source ID {source_id}")
                return source_id
    print(
        f"[DEBUG]   No match found. Using Default Source ID {DEFAULT_INCOME_SOURCE_ID}"
    )
    return DEFAULT_INCOME_SOURCE_ID


def decode_file(file_content: bytes) -> str:
    """Attempt to decode bytes using common encodings."""
    encodings = ["utf-8", "windows-1250", "iso-8859-2", "cp1252", "latin1"]
    for enc in encodings:
        try:
            return file_content.decode(enc)
        except UnicodeDecodeError:
            continue
    # If all fail, try utf-8 with replacement to at least not crash, though data might be ugly
    logger.warning("All encodings failed. Falling back to utf-8 with replacement.")
    return file_content.decode("utf-8", errors="replace")


def process_csv_import(
        db: Session,
        file_content: bytes,
        bank_name: str,
        user_id: int,
        currency: str = "INR",
):
    bank_name = bank_name.lower()
    if bank_name not in BANK_MAPPINGS:
        raise ValueError(f"Bank '{bank_name}' not supported.")

    mapping = BANK_MAPPINGS[bank_name]

    # 1. Decode content
    decoded_file = decode_file(file_content)

    # 2. Detect delimiter
    first_line = decoded_file.split("\n")[0]
    delimiter = ","
    if ";" in first_line and first_line.count(";") > first_line.count(","):
        delimiter = ";"

    # 3. Normalize headers (FIXES DATA LOSS)
    headers, remaining_csv = normalize_headers(decoded_file, delimiter)

    csv_reader = csv.DictReader(
        io.StringIO(remaining_csv),
        fieldnames=headers,
        delimiter=delimiter
    )

    success_count = 0
    errors = []

    for row in csv_reader:
        try:
            # Skip empty rows
            if not any(row.values()):
                continue

            # 4. Parse Date
            date_col = mapping["date"]
            date_fmt = mapping.get("date_format")
            txn_date = parse_date(row.get(date_col, ""), date_fmt)

            # 5. Parse Description
            desc_col = mapping.get("description")
            description = row.get(desc_col, "").strip()

            # 6. Get the Description and combine them
            desc_col = mapping.get("description")
            full_description = build_full_description(row, desc_col)

            # 7. Determine Amount & Type
            amount = 0.0
            is_credit = False

            if "debit" in mapping and "credit" in mapping:
                debit_str = row.get(mapping["debit"], "").replace(",", "").strip()
                credit_str = row.get(mapping["credit"], "").replace(",", "").strip()

                if debit_str:
                    amount = float(debit_str)
                    is_credit = False
                elif credit_str:
                    amount = float(credit_str)
                    is_credit = True

            elif "amount" in mapping and "type" in mapping:
                amt_str = row.get(mapping["amount"], "").replace(",", "").strip()
                type_str = row.get(mapping["type"], "").lower()
                amount = float(amt_str)
                is_credit = "cr" in type_str

            elif "amount" in mapping:
                amt_str = row.get(mapping["amount"], "").replace(",", "").replace(" ", "")
                amount = float(amt_str)

                if amount >= 0:
                    is_credit = True
                else:
                    is_credit = False
                    amount = abs(amount)

            # 8. Persist
            if is_credit:
                source_id = determine_income_source(full_description)
                income_data = IncomeCreate(
                    user_id=user_id,
                    source_id=source_id,
                    amount=amount,
                    currency=currency,
                    earned_date=txn_date,
                )
                create_income(db, income_data)
            else:
                cat_id = determine_category(full_description)
                expense_data = ExpenseCreate(
                    user_id=user_id,
                    category_id=cat_id,
                    amount=amount,
                    currency=currency,
                    spent_date=txn_date,
                )
                create_expense(db, expense_data)

            success_count += 1

        except Exception as e:
            logger.exception(f"Error processing row: {row}")
            errors.append(str(e))

    return {
        "status": "success",
        "processed": success_count,
        "errors": errors,
    }
