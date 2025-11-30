import sqlite3
from datetime import date

conn = sqlite3.connect('Quest.db')
cursor = conn.cursor()
print(type(date.today()))
cursor.execute("INSERT INTO Quest VALUES (?, ?, ?, '', ?)", ('quest_text[0]', 'quest_text[1]', 'quest_text[2]', str(date.today()),))
#cursor.execute("SELECT last_insert_rowid();")
#cursor.execute('DELETE FROM Quest WHERE rowid = ?', (3,))
#cursor.execute(f"UPDATE Quest SET {'Priority'} = ? WHERE rowid = ?", (2, 1, ))
cursor.execute("SELECT rowid, * FROM Quest")
s=cursor.fetchall()
for x in s:
	print(x)
conn.commit()
conn.close()
#cursor.execute("INSERT INTO Quest VALUES (?, ?, ?, ?, ?)",(4, 2, "asd", "ad", "asd"))