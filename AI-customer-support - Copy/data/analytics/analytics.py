import pandas as pd

df = pd.read_csv("../data/complaints.csv")

print("\n===== COMPLAINT ANALYTICS =====")

print("\nTotal Complaints:")
print(len(df))

print("\nComplaints by Category:")
print(df["category"].value_counts())

print("\nComplaints by Urgency:")
print(df["urgency"].value_counts())

print("\nComplaints by Department:")
print(df["department"].value_counts())
