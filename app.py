from flask import Flask, jsonify
from nse import NSE
from datetime import datetime
import traceback

app = Flask(__name__)

# NSE() needs a download folder for cookies/cache. "." = current directory.
# server=True tells the library it's running on a hosted server (not local machine).
nse = NSE(download_folder=".", server=True)


@app.route("/")
def home():
    return jsonify({
        "status": "operational",
        "endpoints": {
            "/breadth/<index>": "Advance/Decline breadth. e.g. /breadth/NIFTY 50 or /breadth/NIFTY BANK",
            "/pcr/<symbol>": "PCR + Max Pain. symbol = nifty or banknifty"
        }
    })


@app.route("/breadth/<index_name>")
def breadth(index_name):
    try:
        data = nse.advanceDecline(index=index_name.upper())
        return jsonify({"status": "success", "index": index_name.upper(), "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500


@app.route("/pcr/<symbol>")
def pcr(symbol):
    try:
        symbol = symbol.lower()  # 'nifty' or 'banknifty'

        # Let optionChain auto-resolve the nearest valid OPTIONS expiry
        # (not the futures expiry - they differ: options expire weekly, futures monthly)
        raw_chain = nse.optionChain(symbol=symbol)
        expiry_str = raw_chain["records"]["expiryDates"][0]
        nearest_expiry = datetime.strptime(expiry_str, "%d-%b-%Y")

        compiled = nse.compileOptionChain(symbol=symbol, expiryDate=nearest_expiry)
        max_pain = NSE.maxpain(raw_chain, nearest_expiry)

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "expiry": expiry_str,
            "max_pain": max_pain,
            "compiled_summary": compiled
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500


from nsepython import nse_fiidii

@app.route("/fiidii")
def fiidii():
    try:
        data = nse_fiidii("list")  # returns raw list format

        result = {}
        for row in data:
            category = "fii" if "FII" in row["category"] else "dii"
            result[category] = {
                "buyValue": float(row["buyValue"]),
                "sellValue": float(row["sellValue"]),
                "netValue": float(row["netValue"]),
                "date": row["date"]
            }

        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
