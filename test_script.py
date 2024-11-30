import pandas as pd 


# read cibc csv file
cibc_input_df = pd.read_csv("./cibc.csv", header=0, names=["Date", "Info", "Outgoing", "Incoming"])

# correct date column types
# cibc_input_df["Info"] = cibc_input_df["Info"].astype("string", errors='raise')
cibc_input_df["Date"] = pd.to_datetime(cibc_input_df["Date"]).dt.date


# generate income and expenses dataframes
cibc_income_df = cibc_input_df[cibc_input_df["Incoming"].notna()].drop("Outgoing", axis="columns") 
cibc_expense_df = cibc_input_df[cibc_input_df["Outgoing"].notna()].drop("Incoming", axis="columns")




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


# consolidate income and expenses into one dataframe
income_df = pd.concat([cibc_income_df, rbc_income_df]).sort_values(by=["Date"])
expense_df = pd.concat([cibc_expense_df, rbc_expense_df]).sort_values(by=["Date"])


# output to csv
saveFile = './output/output.xlsx'
writer = pd.ExcelWriter(saveFile, date_format="yyyy-mm-dd")
income_df.to_excel(writer, sheet_name="Income", index=False)
expense_df.to_excel(writer, sheet_name="Expenses", index=False)
writer.close()


