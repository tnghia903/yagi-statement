import csv
import os
import re
from typing import Callable, Dict, List, Optional

import pdfplumber
from pdfplumber.page import Page

from models import Transaction


def __get_offset_name_from_transaction_detail(transaction_detail: str) -> str | None:
    # Define the regex pattern for Vietnamese names
    pattern = r"\b([A-Z]+(?:\s[A-Z]+){1,})\b"

    # Use re.search to find the first occurrence of a Vietnamese name
    match = re.search(pattern, transaction_detail)

    if match:
        return match.group(1)
    return None


def __format_to_dd_mm_yyyyy(date: str) -> str:
    date_list = date.split("/")
    month, day, year = date_list
    day = int(day)
    month = int(month)

    formatted_day = f"0{day}" if day < 10 else f"{day}"
    formatted_month = f"0{month}" if month < 10 else f"{month}"

    return f"{formatted_day}/{formatted_month}/{year}"


def __extract_data_to_transaction(
    file_path: str,
    clean_row: Callable,
    map_to_transaction: Callable,
    first_row_index: int = 1,
    get_table_settings: Optional[Callable] = None,
) -> List[Transaction]:
    pdf = pdfplumber.open(file_path)
    num_of_page = len(pdf.pages)
    raw_rows = []
    for i in range(0, 1):
        print(f"{file_path} - Processing page: {i}")
        p: Page = pdf.pages[i]
        table = p.extract_table(
            table_settings=None if get_table_settings is None else get_table_settings(
                p)
        )
        if table is not None:
            raw_rows.extend(table[first_row_index:])
    cleaned_row = clean_row(raw_rows)
    transactions_data = [map_to_transaction(row) for row in cleaned_row]
    return transactions_data


def __get_table_settings_vcb(page: Page) -> Dict[str, str | List[int]]:
    return {
        "vertical_strategy": "lines",
        "horizontal_strategy": "explicit",
        "explicit_horizontal_lines": [x["top"] for x in page.edges],
    }


def __clean_row_vcb(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]

    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 0:
                cleaned_row[i].extend(item.split("\n"))
            elif j == 2:
                cleaned_row[i].append(item.replace(".", ""))
            elif j == 4:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 1 or j == 3:
                continue
            else:
                cleaned_row[i].append(item)
    return cleaned_row


def __clean_row_vcb_2(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]

    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 2:
                cleaned_row[i].append(item.replace(".", ""))
            elif j == 3:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 0:
                continue
            else:
                cleaned_row[i].append(item)
    return cleaned_row


def __clean_row_bidv(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]
    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 3:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 2:
                cleaned_row[i].append(item.replace(".", ""))
            elif j == 0:
                continue
            else:
                cleaned_row[i].append(item)

    return cleaned_row


def __clean_row_ctg(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]
    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 1:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 2:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 3:
                cleaned_row[i].append(item.replace(".", ""))
            elif j == 0:
                continue
            else:
                cleaned_row[i].append(item)

    return cleaned_row


def __clean_row_cash(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]
    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 2:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 3:
                cleaned_row[i].append(item.replace(" ", ""))
            elif j == 0 or j == 4 or j == 5 or j == 6:
                continue
            else:
                cleaned_row[i].append(item)

    return cleaned_row


def __clean_row_agr(raw_rows: List[str]) -> List[List[str]]:
    cleaned_row = [[] for i in range(len(raw_rows))]
    for i, row in enumerate(raw_rows):
        for j, item in enumerate(row):
            if j == 1:
                cleaned_row[i].append(item.replace("\n", " "))
            elif j == 3:
                cleaned_row[i].append(item.replace(",", ""))
            elif j == 2 or j == 4 or j == 5:
                continue
            else:
                cleaned_row[i].append(item)

    return cleaned_row


def __map_bidv_to_transaction(row: List[str]) -> Transaction:
    transaction_date = row[0]
    credit = int(row[1])
    transaction_details = row[2]
    offset_name = __get_offset_name_from_transaction_detail(
        transaction_details)
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "BIDV"
    )


def __map_cash_to_transaction(row: List[str]) -> Transaction:
    transaction_date = __format_to_dd_mm_yyyyy(row[0])
    credit = int(row[2])
    transaction_details = row[1]
    offset_name = __get_offset_name_from_transaction_detail(
        transaction_details)
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "CASH"
    )


def __map_agr_to_transaction(row: List[str]) -> Transaction:
    transaction_date = row[0]
    credit = int(row[2])
    transaction_details = row[1]
    offset_name = __get_offset_name_from_transaction_detail(
        transaction_details)
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "AGRIBANK"
    )


def __map_ctg_to_transaction(row: List[str]) -> Transaction:
    transaction_date = row[0]
    credit = int(row[2])
    transaction_details = row[1]
    offset_name = row[3]
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "VIETINBANK"
    )


def __map_vcb_to_transaction(row: List[str]) -> Transaction:
    transaction_date = row[0]
    credit = int(row[2])
    transaction_details = row[3]
    offset_name = __get_offset_name_from_transaction_detail(
        transaction_details)
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "VIETCOMBANK"
    )


def __map_vcb_to_transaction_2(row: List[str]) -> Transaction:
    transaction_date = row[0]
    credit = int(row[1])
    transaction_details = row[2]
    offset_name = __get_offset_name_from_transaction_detail(
        transaction_details)
    return Transaction(
        offset_name, transaction_date, credit, transaction_details, "VIETCOMBANK"
    )


def extract_data_vcb(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path,
        __clean_row_vcb,
        __map_vcb_to_transaction,
        1,
        __get_table_settings_vcb,
    )


def extract_data_vcb_2(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path, __clean_row_vcb_2, __map_vcb_to_transaction_2, 1
    )


def extract_data_ctg(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path, __clean_row_ctg, __map_ctg_to_transaction, 2
    )


def extract_data_agr(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path, __clean_row_agr, __map_agr_to_transaction, 1
    )


def extract_data_cash(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path, __clean_row_cash, __map_cash_to_transaction, 4
    )


def extract_data_bidv(file_path: str) -> List[Transaction]:
    return __extract_data_to_transaction(
        file_path, __clean_row_bidv, __map_bidv_to_transaction, 1
    )


def extract_csv_data(csv_output_file_path: str, data: List[Transaction]):
    fieldnames = data[0].to_dict().keys()
    with open(csv_output_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data rows
        for transaction in data:
            writer.writerow(transaction.to_dict())


def extract_data_treasury(file_path: str) -> List[Transaction]:
    pdf = pdfplumber.open(file_path)
    num_of_page = len(pdf.pages)
    transaction_list = []
    for i in range(0, 10):
        print(f"{file_path} - Processing page: {i}")
        p: Page = pdf.pages[i]
        text = p.extract_text()
        data = text.split("\n")
        for row in data:
            if 'Người phát lệnh' in row:
                offset_name = row.split(": ")[-1]
            if 'Ngày, giờ gửi (nhận)' in row:
                transaction_date = row.split(": ", 2)[-1]
            if 'Số tiền bằng số' in row:
                match = re.search(r':\s*([\d.]+)', row)
                if match:
                    credit = int(match.group(1).replace(".", ""))
            if 'Nội dung' in row:
                transaction_details = row.split(": ")[-1]
            if 'Ngân hàng chịu phí' in row:
                source = f"TREASURY - {row.split(': ')[-1]}"

        transaction = Transaction(
            offset_name, transaction_date, credit, transaction_details, source
        )
        transaction_list.append(transaction)
    return transaction_list
