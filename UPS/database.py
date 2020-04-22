import psycopg2

def connectDB():
    db = psycopg2.connect(database = 'cugnezod', user = 'cugnezod', password = 'WY3VYXBCtpI3WhLKNbL_tP1xcW1UGmya', host = 'drona.db.elephantsql.com', port = '5432')
    return db

 ######## truck ##########   
def addTruck(db, i):
    cursor = db.cursor()
    sql = "INSERT INTO users_truck VALUES (%s, 'idle');"
    cursor.execute(sql, i)
    db.commit()

def updateTruckStatus(db, truckid, status):
    cursor = db.cursor()
    sql = "UPDATE users_truck SET status = %s WHERE id = %s;"
    cursor.execute(sql, (status, truckid))
    db.commit()
    
def findIdleTruck(db):
    cursor = db.cursor()
    sql = "SELECT FROM users_truck WHERE status = 'idle';"
    cursor.execute(sql)
    res = cursor.fetchall()
    if res:
        return res[0]
    else:
        return 0

######## package ##########

def addPackage(db,description,pckid,status,whid,ownerName):
    cursor=db.cursor()
    sql="INSERT INTO users_package VALUES ();"
    cursor.execute()
    db.commit()









'''
if __name__ == '__main__':
    conn=connectDB()
    createTableTruck(conn)
'''
