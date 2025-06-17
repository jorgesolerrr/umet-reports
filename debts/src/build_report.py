import json
import pandas as pd
from datetime import datetime

PATH_DATA = "data/17-6-25_1035.json"

def get_data():
    with open(PATH_DATA, "r") as file:
        data = json.load(file)
    return data["data"]


def export_data(df):
    df.to_excel(f"debts/reports/deudas-{datetime.now().strftime('%d-%m-%Y_%H%M')}.xlsx", index=False)

def build_report(data):
    df = pd.DataFrame(data)
    export_data(df)
    
    
def main():
    data = get_data()
    build_report(data)

if __name__ == "__main__":
    main()