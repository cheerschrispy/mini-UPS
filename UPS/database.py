import psycopg2
cursor
def connectDB():
    db = psycopg2.connect(database = 'cugnezod', user = 'cugnezod', password = 'WY3VYXBCtpI3WhLKNbL_tP1xcW1UGmya', host = 'drona.db.elephantsql.com', port = '5432')
    return db
    
def addTruck(db, i):
    cursor = db.cursor()
    sql = "INSERT INTO trucks VALUES (%s, 'idle');"
    cursor.execute(sql, i)
    db.commit()

def updateTruckStatus(db, truckid, status):
    cursor = conn.cursor()
    sql = "UPDATE trucks SET status = %s WHERE truckid = %s;"
    cursor.execute(sql, (status, truckid))
    db.commit()
    
def findIdleTruck(db):
    cursor = db.cursor()
    sql = "SELECT FROM trucks WHERE status = 'idle';"
    cursor.execute(sql)
    res = cursor.fetchall()
    if res:
        return res[0]
    else
        return 0

'''
if __name__ == '__main__':
    conn=connectDB()
    createTableTruck(conn)
'''
