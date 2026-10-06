import duckdb

con = duckdb.connect()  # in-memory session
con.sql("ATTACH 'setel.duckdb' AS setel (READ_ONLY)")
con.sql("USE setel")
con.sql("CALL start_ui()")
input("DuckDB UI running. Press Enter to stop...")