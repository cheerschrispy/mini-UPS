import psycopg2

def connectDB():
    db = psycopg2.connect(database = 'cugnezod', user = 'cugnezod', password = 'WY3VYXBCtpI3WhLKNbL_tP1xcW1UGmya', host = 'drona.db.elephantsql.com', port = '5432')
    return db

######### truck ##########   
def addTruck(db, i):
    cursor = db.cursor()
    sql = "INSERT INTO users_truck VALUES (%s, 'idle', -1);"
    cursor.execute(sql, i)
    db.commit()

def updateTruckStatus(db, truckid, status, whid = -1):
    cursor = db.cursor()
    sql1 = "UPDATE users_truck SET status = %s WHERE id = %s;"
    cursor.execute(sql1, (status, truckid))
    sql2 = "UPDATE users_truck SET whid = %s WHERE id = %s;"
    cursor.execute(sql1, (whid, truckid))
    db.commit()
    
def findIdleTruck(db):
    cursor = db.cursor()
    sql = "SELECT id FROM users_truck WHERE status = 'idle';"
    cursor.execute(sql)
    res = cursor.fetchall()
    if res:
        return res[0]
    else:
        return 0

def getWhid(db, truckid):
    cursor = db.cursor()
    sql = "SELECT whid FROM users_truck WHERE truckid = %s;"
    cursor.execute(sql, truckid)
    res = cursor.fetchall()
    if res:
        return res[0]
    else:
        print("Cannot get the correct whid!")
        return -1
    
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
