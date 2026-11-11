
import pandas as pd
import dtale

# Load actual sales dataset
df = pd.read_csv("sales_data.csv")

print("Dataset loaded successfully!")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# Start D-Tale dashboard
d = dtale.show(
    df,
    host="127.0.0.1",
    port=40000
)

print("D-Tale URL:", d._main_url)

# Keep server running
input("Press Enter to stop D-Tale...")
