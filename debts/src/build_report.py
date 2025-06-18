import json
import pandas as pd
from datetime import datetime

PATH_DATA = "data/17-6-25_1035.json"


def get_data():
    with open(PATH_DATA, "r") as file:
        data = json.load(file)
    return data["data"]


def export_data(df):
    name = f"deudas-{datetime.now().strftime('%d-%m-%Y_%H%M')}.xlsx"
    path = f"debts/reports/{name}"
    df.to_excel(path, index=False)
    return name


def build_report(data):
    df = pd.DataFrame(data)
    name = export_data(df)

    with open(f"debts/reports/{name}", "rb") as file:
        file_content = file.read()

    return {"file": file_content, "name": name}


def main():
    data = get_data()
    build_report(data)


if __name__ == "__main__":
    main()
