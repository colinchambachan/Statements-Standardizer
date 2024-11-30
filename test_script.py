import pandas as pd 


# read csv file
cibc_input_df = pd.read_csv("./cibc.csv", header=0, names=["Date", "Info", "Outgoing", "Incoming"])

# correct date column types
# cibc_input_df["Info"] = cibc_input_df["Info"].astype("string", errors='raise')
cibc_input_df["Date"] = pd.to_datetime(cibc_input_df["Date"])


# generate income and expenses dataframes
cibc_income_df = cibc_input_df[cibc_input_df["Incoming"].notna()].drop("Outgoing", axis="columns") 
cibc_expense_df = cibc_input_df[cibc_input_df["Outgoing"].notna()].drop("Incoming", axis="columns")




