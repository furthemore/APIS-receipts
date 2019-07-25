from flask import Flask, request, jsonify
from escpos import *

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/print/drawer")
def print_cash():
    reference = request.args.get('reference', None)
    charity = request.args.get('charity', 0)
    organisation = request.args.get('organisation', 0)
    total = request.args.get('total', 0)
    tendered = request.args.get('tendered', 0)
    change = request.args.get('change', 0)

    p = printer.Network("10.0.18.40")
    p.cashdraw(2)
    #p.image('logo.gif')
    p.text("Thank you for your payment\n\n")
    p.text("Charity donation:  ${0}\n".format(charity))
    p.text("Org. donation:     ${0}\n\n".format(organisation))
    p.text("            Total: ${0}\n".format(total))
    p.text("         Tendered: ${0}\n".format(tendered))
    p.text("           Change: ${0}\n".format(change))

    p.text("Reference: {0}".format(reference))
    p.text("\n\n\n\n\n\n")
    p.cut()

    return jsonify({'success' : 'true'})

@app.route("/jgwentworth")
def open_drawer():
    p = printer.Network("10.0.18.40")
    p.cashdraw(2)
    return jsonify({'success' : 'true'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context='adhoc')
