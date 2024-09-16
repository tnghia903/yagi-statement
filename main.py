import json
import os
import subprocess
from redis import Redis

from extract_data import (
    extract_csv_data,
    extract_data_agr,
    extract_data_bidv,
    extract_data_cash,
    extract_data_ctg,
    extract_data_treasury,
    extract_data_vcb,
    extract_data_vcb_2,
)


r = Redis(host="redis", port=6379, db=0, decode_responses=True)


data_vcb = extract_data_vcb(
    "statements/sao-ke-vcb.pdf",
)
data_vcb_2 = extract_data_vcb_2("statements/sao-ke-vcb-2.pdf")
data_ctg = extract_data_ctg("statements/sao-ke-ctg.pdf")
data_agr = extract_data_agr("statements/sao-ke-agr.pdf")
data_cash = extract_data_cash("statements/sao-ke-cash.pdf")
data_bidv = extract_data_bidv("statements/sao-ke-bidv.pdf")

# If you want to try OCR yourself, comment the following code
data_treasury = extract_data_treasury("statements/sao-ke-treasury-ocr.pdf")

# If you want to try OCR yourself, uncomment the following code
# os.makedirs("ocr", exist_ok=True)
# if os.path.isfile("ocr/sao-ke-treasury.pdf"):
#     data_treasury = extract_data_treasury("ocr/sao-ke-treasury.pdf")
# else:
#     subprocess.run(["ocrmypdf", "-l", "vie", "statements/sao-ke-treasury.pdf",
#                    "ocr/sao-ke-treasury.pdf"], check=True)
#     data_treasury = extract_data_treasury("ocr/sao-ke-treasury.pdf")

data = (
    data_vcb + data_vcb_2 + data_ctg + data_agr + data_cash + data_bidv + data_treasury
)
transactions = [t.to_dict() for t in data]
data_json = json.dumps(transactions)
r.set("transactions", data_json)

# Export to CSV
# extract_csv_data("output.csv", data)
