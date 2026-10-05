import duckdb
import pandas as pd

con = duckdb.connect("setel.duckdb")

df_partner = pd.read_csv("data/partner_data.csv")
df_orders = pd.read_excel("data/List of orders - jun - sep.xlsx")

con.execute("CREATE OR REPLACE TABLE partner AS SELECT * FROM df_partner")
con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM df_orders")

print(con.sql("SHOW TABLES"))
print(con.sql("SELECT * FROM partner LIMIT 5"))
print(con.sql("SELECT * FROM orders LIMIT 5"))