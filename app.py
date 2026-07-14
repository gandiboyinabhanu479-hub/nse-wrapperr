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
        expiry_list = nse.getFuturesExpiry(index=symbol)
        nearest_expiry = datetime.strptime(expiry_list[0], "%d-%b-%Y")

        compiled = nse.compileOptionChain(symbol=symbol, expiryDate=nearest_expiry)
        raw_chain = nse.optionChain(symbol=symbol, expiry_date=nearest_expiry)
        max_pain = NSE.maxpain(raw_chain, nearest_expiry)

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "expiry": expiry_list[0],
            "max_pain": max_pain,
            "compiled_summary": compiled
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
