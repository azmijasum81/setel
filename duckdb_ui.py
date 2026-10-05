import duckdb

con = duckdb.connect("setel.duckdb")
con.sql("CALL start_ui()")
input("UI is running. Press Enter to stop...")