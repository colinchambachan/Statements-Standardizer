import pandas as pd
import argparse
import os

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

    return rbc_income_df, rbc_expense_df


def write_to_xlsx(df_sheet_map):
    # output to xlsx
    if not os.path.exists("output"):
        os.makedirs("output")

    saveFile = './output/output.xlsx'
    writer = pd.ExcelWriter(saveFile, date_format="yyyy-mm-dd")
    for sheet_name, df in df_sheet_map.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.close()


if __name__ == "__main__":
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bank",
        nargs="*",  # accepts zero or more arguments
        choices=["cibc", "rbc"],  # restrict choices
        default=["cibc", "rbc"],  # default to both if nothing is specified
        help="Specify which bank statment(s) to process: cibc, rbc, or both (default)."
    )
    args = parser.parse_args()

    # store income and expense dataframes for each bank
    incomes = []
    expenses = []

    print("[INFO] Initializing script...")
    # handle each banks transaction processining
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

    # write dataframes to xlsx
    sheet_map = {"Income": income_df, "Expenses": expense_df}
    print("[INFO] Writing to files output.xlsx...")
    write_to_xlsx(sheet_map)
    print("[SUCCESS] Script complete")
    


