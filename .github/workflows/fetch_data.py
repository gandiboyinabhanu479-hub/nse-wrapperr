from nse import NSE
from datetime import datetime
import json
import os
import traceback

nse = NSE(download_folder=".", server=True)
os.makedirs("data", exist_ok=True)


def fetch_breadth():
    try:
        data = nse.advanceDecline(index="NIFTY 50")
        result = {"status": "success", "index": "NIFTY 50", "data": data}
    except Exception as e:
        result = {"status": "error", "message": str(e), "trace": traceback.format_exc()}
    with open("data/breadth.json", "w") as f:
        json.dump(result, f)


def fetch_pcr():
    try:
        symbol = "nifty"
        raw_chain = nse.optionChain(symbol=symbol)
        expiry_str = raw_chain["records"]["expiryDates"][0]
        nearest_expiry = datetime.strptime(expiry_str, "%d-%b-%Y")

        compiled = nse.compileOptionChain(symbol=symbol, expiryDate=nearest_expiry)
        max_pain = NSE.maxpain(raw_chain, nearest_expiry)

        result = {
            "status": "success",
            "symbol": symbol,
            "expiry": expiry_str,
            "max_pain": max_pain,
            "compiled_summary": compiled
        }
    except Exception as e:
        result = {"status": "error", "message": str(e), "trace": traceback.format_exc()}
    with open("data/pcr.json", "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    fetch_breadth()
    fetch_pcr()
