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
        if (
            (key.startswith("__extra_") | key.startswith("Benefeciary"))
            and value
            and value.strip()
        ):
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


def preview_csv_import(
    file_content: bytes,
    bank_name: str,
    currency: str = "INR",
) -> list[dict]:
    """
    Parses CSV and returns a list of potential transactions with proposed categories/sources.
    Does NOT save to DB.
    """
    bank_name = bank_name.lower()
    if bank_name not in BANK_MAPPINGS:
        raise ValueError(f"Bank '{bank_name}' not supported.")

    mapping = BANK_MAPPINGS[bank_name]

    # 1. Decode & Normalize
    decoded_file = decode_file(file_content)
    first_line = decoded_file.split("\n")[0]
    delimiter = (
        ";"
        if ";" in first_line and first_line.count(";") > first_line.count(",")
        else ","
    )
    headers, remaining_csv = normalize_headers(decoded_file, delimiter)

    csv_reader = csv.DictReader(
        io.StringIO(remaining_csv), fieldnames=headers, delimiter=delimiter
    )

    preview_data = []

    for row in csv_reader:
        if not any(row.values()):
            continue

        try:
            # Parse Date
            date_col = mapping["date"]
            date_fmt = mapping.get("date_format")
            txn_date = parse_date(row.get(date_col, ""), date_fmt)

            # Parse Description
            desc_col = mapping.get("description")
            full_description = build_full_description(row, desc_col)

            # Determine Amount & Type
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
                amt_str = (
                    row.get(mapping["amount"], "")
                    .replace(",", "")
                    .replace(" ", "")
                    .replace("\xa0", "")
                )
                amount = float(amt_str)
                if amount >= 0:
                    is_credit = True
                else:
                    is_credit = False
                    amount = abs(amount)

            # Propose Category/Source
            category_id = None
            source_id = None

            if is_credit:
                source_id = determine_income_source(full_description)
            else:
                category_id = determine_category(full_description)

            preview_data.append(
                {
                    "date": txn_date.strftime("%Y-%m-%d"),
                    "description": full_description,
                    "amount": amount,
                    "currency": currency,
                    "type": "income" if is_credit else "expense",
                    "category_id": category_id,
                    "source_id": source_id,
                    # Helper for frontend to know which field to show
                    "original_row": row,
                }
            )

        except Exception as e:
            logger.error(f"Error parsing row for preview: {e}")
            continue

    return preview_data


def update_category_rules_file(updates: list[dict]):
    """
    Updates bank_config.py with new rules.
    updates format: [{"id": 123, "keyword": "new_keyword", "type": "category"|"source"}]
    """
    import os

    config_path = "backend/configurations/bank_config.py"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at {config_path}")
        return

    with open(config_path, "r") as f:
        content = f.read()

    modified = False

    for update in updates:
        rule_type = update.get("type")  # 'category' or 'source'
        target_id = update.get("id")
        keyword = update.get("keyword")

        if not keyword:
            continue

        # VERY BASIC string manipulation to avoid complex AST rewriting that strips comments
        # Looking for pattern:  <id>: [ ... ]
        # We will attempt to insert the keyword into the list for that ID.

        # Determine variable name
        var_name = (
            "CATEGORY_RULES" if rule_type == "category" else "INCOME_SOURCE_RULES"
        )

        # We need to find the start of the dict, then the key.
        # This is a bit brittle but regex can help.

        # Regex to find: <id>: [ ... ]
        # We want to match:     12: [ ..., "existing" ],
        # And replace with:     12: [ ..., "existing", "new_keyword" ],

        # Regex explanation:
        # 1. Match the key (e.g. 12 or 6) followed by : and optional whitespace
        # 2. Match [
        # 3. Match content inside (lazy)
        # 4. Match ]

        # Check if we are inside the correct variable block?
        # Ideally we only search within the relevant block, but IDs are unique per dict usually in this file?
        # Actually IDs might collide between Category and Income dicts (1, 2, etc).
        # So we MUST find the dict block first.

        start_idx = content.find(f"{var_name} = {{")
        if start_idx == -1:
            continue

        # Find the end of this dict (approximate, looking for next variable or file end)
        # Assuming brace matching is hard, let's limit search window?
        # Or just use the fact that the key indentation is likely 4 spaces.

        # Better approach: Read lines, state machine.
        lines = content.splitlines()
        new_lines = []
        in_target_dict = False

        for line in lines:
            if line.startswith(f"{var_name} = {{"):
                in_target_dict = True
            elif in_target_dict and line.startswith("}"):
                in_target_dict = False

            if in_target_dict:
                # Check for key match: "    6: ["
                stripped = line.strip()
                if stripped.startswith(f"{target_id}: ["):
                    # Found the line!
                    # Check if it's a single line list "12: []," or multi-line.
                    if "]" in line:
                        # Single line or end of multi-line on same line?
                        # e.g. 12: [],  -> insert inside
                        parts = line.split("]")
                        # Insert before the last ]
                        # line = '    12: ["a", "b"],'
                        # parts[0] = '    12: ["a", "b"'
                        new_line = f'{parts[0]}, "{keyword}"],{parts[1] if len(parts) > 1 else ""}'
                        # Clean up potential double commas
                        new_line = new_line.replace(",,", ",").replace("[,", "[")
                        new_lines.append(new_line)
                    else:
                        # Multi-line array start
                        new_lines.append(line)
                        # We can just append the new keyword as the first item in the list on next line
                        new_lines.append(f'        "{keyword}",')

                    modified = True
                    continue  # Skip adding the original line

            new_lines.append(line)

        content = "\n".join(new_lines)

    if modified:
        with open(config_path, "w") as f:
            f.write(content)

        # TOUCH RESTART FLAG
        with open(".restart_required", "w") as f:
            f.write("Restart required due to config update.")


def confirm_import_and_learn(
    db: Session,
    user_id: int,
    transactions: list[dict],
):
    """
    Saves confirmed transactions and learns new rules.
    transactions: list of dicts with 'date', 'amount', 'type', 'category_id', 'source_id', 'description'
    """
    count = 0
    updates_to_learn = []

    for txn in transactions:
        amount = float(txn["amount"])
        currency = txn.get("currency", "INR")
        # Parse date if it's string
        t_date = txn["date"]
        if isinstance(t_date, str):
            t_date = datetime.strptime(t_date, "%Y-%m-%d")

        if txn["type"] == "income":
            inc = IncomeCreate(
                user_id=user_id,
                source_id=txn.get("source_id", DEFAULT_INCOME_SOURCE_ID),
                amount=amount,
                currency=currency,
                earned_date=t_date,
            )
            create_income(db, inc)

            # Learn?
            # We need to know if this was a manual override.
            # Ideally frontend sends a flag, or we re-check current rule.
            # simpler heuristic: Check if current rules would predict this.
            # usage: "learn_keyword": "zomato" (optional field from frontend)
            if txn.get("learn_keyword"):
                updates_to_learn.append(
                    {
                        "type": "source",
                        "id": txn["source_id"],
                        "keyword": txn["learn_keyword"],
                    }
                )

        else:
            exp = ExpenseCreate(
                user_id=user_id,
                category_id=txn.get("category_id", DEFAULT_CATEGORY_ID),
                amount=amount,
                currency=currency,
                spent_date=t_date,
            )
            create_expense(db, exp)

            if txn.get("learn_keyword"):
                updates_to_learn.append(
                    {
                        "type": "category",
                        "id": txn["category_id"],
                        "keyword": txn["learn_keyword"],
                    }
                )

        count += 1

    if updates_to_learn:
        update_category_rules_file(updates_to_learn)

    return {"status": "success", "processed": count, "learned": len(updates_to_learn)}
