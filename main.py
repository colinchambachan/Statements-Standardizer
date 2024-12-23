import pandas as pd
import argparse
import os
from openpyxl import load_workbook

def cibc_transform():
    # read cibc csv file
    cibc_input_df = pd.read_csv("./cibc.csv", header=0, names=["Date", "Info", "Outgoing", "Incoming"])

    # correct date column types
    cibc_input_df["Date"] = pd.to_datetime(cibc_input_df["Date"]).dt.date

    # generate income and expenses dataframes
    cibc_income_df = cibc_input_df[cibc_input_df["Incoming"].notna()].drop("Outgoing", axis="columns") 
    cibc_expense_df = cibc_input_df[cibc_input_df["Outgoing"].notna()].drop("Incoming", axis="columns")

    return cibc_income_df, cibc_expense_df


def rbc_transform():
    # read rbc csv file
    rbc_input_df = pd.read_csv("./rbc.csv", index_col=False)

    # keep only necessary columns
    rbc_input_df = rbc_input_df.drop(columns=["Account Type", "Account Number", "Cheque Number", "USD$"])
    rbc_input_df["Description 2"] = rbc_input_df["Description 2"].fillna( rbc_input_df["Description 1"])
    rbc_input_df = rbc_input_df.drop(columns=["Description 1"])
    rbc_input_df = rbc_input_df.rename(columns={"Transaction Date": "Date", "Description 2": "Info"})
    rbc_input_df["Date"] = pd.to_datetime(rbc_input_df["Date"]).dt.date

    # generate income and expenses dataframes
    rbc_income_df = rbc_input_df[rbc_input_df["CAD$"] > 0].rename(columns={"CAD$": "Incoming"})
    rbc_expense_df = rbc_input_df[rbc_input_df["CAD$"] < 0].rename(columns={"CAD$": "Outgoing"})
    rbc_expense_df["Outgoing"] = rbc_expense_df["Outgoing"].abs()
    
    return rbc_income_df, rbc_expense_df


def write_to_xlsx(df_sheet_map):
    # output to xlsx
    if not os.path.exists("output"):
        os.makedirs("output")
    saveFile = './output/output.xlsx'
    writer = pd.ExcelWriter(saveFile, date_format="mm-dd-yyyy")
    for sheet_name, df in df_sheet_map.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False, engine="openpyxl")
    writer.close()


def format_xslx():
    wb = load_workbook(filename = r'./output/output.xlsx')
    for sheet in wb.worksheets:
        # autosize columns
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter # get column name
            for cell in col:
                try: 
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column].width = adjusted_width
                
        wb.save(r'./output/output.xlsx')


if __name__ == "__main__":
    financial_institutions = ["cibc", "rbc"]
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bank",
        nargs="*",  # accepts zero or more arguments
        choices=financial_institutions,  # restrict choices
        default=financial_institutions,  # default to all if nothing is specified
        help="Specify which bank statement(s) to process: cibc, rbc, or both (default)."
    )
    args = parser.parse_args()

    # store income and expense dataframes for each bank
    incomes = []
    expenses = []

    print("[INFO] Initializing script...")
    # handle each banks transaction processing
    if "cibc" in args.bank:
        print("[INFO] Processing CIBC transactions...")
        cibc_income_df, cibc_expense_df = cibc_transform()
        incomes.append(cibc_income_df)
        expenses.append(cibc_expense_df)

    if "rbc" in args.bank:
        print("[INFO] Processing RBC transactions...")
        rbc_income_df, rbc_expense_df = rbc_transform()
        incomes.append(rbc_income_df)
        expenses.append(rbc_expense_df)
    
    # consolidate all dataframes into one income and expense dataframe
    income_df = pd.concat(incomes).sort_values(by=["Date"])
    expense_df = pd.concat(expenses).sort_values(by=["Date"])


    # write dataframes to xlsx file
    sheet_map = {"Income": income_df, "Expenses": expense_df}
    print("[INFO] Writing to output.xlsx...")
    write_to_xlsx(sheet_map)
    format_xslx()
    
    print("[SUCCESS] Script complete")
    


