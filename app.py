import csv
import requests
from flask import Flask, render_template, request
import locale
app = Flask(__name__)
locale.setlocale(locale.LC_ALL, 'pl_PL')


def save_currency_file():
    response = requests.get(
        "http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    data = response.json()
    rates = data[0]['rates']
    with open('currency.csv', 'w', newline='') as csvfile:
        currency_writer = csv.writer(csvfile, delimiter=';')
        for i in rates:
            currency_writer.writerow(i.values())


def get_currency_code():
    currency_code = []
    with open('currency.csv', 'r', newline='') as csvfile:
        currency_reader = csv.reader(csvfile, delimiter=';')
        for i in currency_reader:
            currency_code.append(i[1])
    return currency_code


def get_currency_rate(currency_code):
    currency_rate = 1
    with open('currency.csv', 'r', newline='') as csvfile:
        currency_reader = csv.reader(csvfile, delimiter=';')
        for i in currency_reader:
            if currency_code == i[1]:
                currency_rate = i[2]
    return currency_rate


def get_currency_exchange(currency_code, currency_count):
    currency_rate = get_currency_rate(currency_code)
    currency_exchange = 0
    try:
        currency_exchange = float(currency_rate) * float(currency_count)
    except:
        print("Niestety to nie jest poprawna ilość: ", currency_count)

    return currency_exchange


@app.route("/get_currency", methods=["POST"])
def get_currency():
    save_currency_file()
    currency_code = get_currency_code()
    return render_template("currency.html", items=currency_code)


@app.route("/currency_calc/", methods=["GET", "POST"])
def currency_calc():
    currency_code = get_currency_code()
    if request.method == 'GET':
        return render_template("currency.html", items=currency_code)
    elif request.method == 'POST':
        currency_count = request.form['currency_count']
        selected_currency_code = request.form['currency']
        curr_value = get_currency_exchange(
            selected_currency_code, currency_count)
        curr_value = locale.format_string('%.2f', curr_value, True)
        return render_template("currency_pay.html", items=currency_code, curr_value=curr_value, selected_currency_code=selected_currency_code, currency_count=currency_count)


if __name__ == "__main__":
    save_currency_file()
    app.run(debug=True)
