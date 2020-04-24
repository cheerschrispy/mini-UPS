import psycopg2

def connectDB():
    db = psycopg2.connect(database = 'cugnezod', user = 'cugnezod', password = 'WY3VYXBCtpI3WhLKNbL_tP1xcW1UGmya', host = 'drona.db.elephantsql.com', port = '5432')
    return db

######### truck ##########   
def addTruck(db, i):
    cursor = db.cursor()
    sql = "INSERT INTO users_truck VALUES (%s, 'idle', -1);"
    cursor.execute(sql, [i])
    db.commit()

def updateTruckStatus(db, truckid, status, whid=-1):
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
        return res[0][0]
    else:
        return 0

def getWhid(db, truckid):
    cursor = db.cursor()
    sql = "SELECT whid FROM users_truck WHERE id = %s;"
    cursor.execute(sql, [truckid])
    res = cursor.fetchall()
    if res:
        return res[0][0]
    else:
        print("Cannot get the correct whid!")
        return -1
    
######## package ##########

def addPackage(db,detail,pckid,whid,ownerName,x,y):
    cursor=db.cursor()
    sql="INSERT INTO users_package(trackingnum,owner,whid,detail,x,y,status) VALUES(%s,%s,%s,%s,%s,%s,'created');"
    cursor.execute(sql,(pckid,ownerName,whid,detail,x,y))
    db.commit()

def updatePackageStatus(db,status,packageid):
    cursor=db.cursor()
    sql="UPDATE users_package SET status=%s WHERE trackingnum=%s;"
    cursor.execute(sql,(status,packageid))
    db.commit()
#update x,y location is done by user in front-end

def getPackageIDFromTruckid(db,truckid):
    cursor = db.cursor()
    whid=getWhid(db,truckid)
    print("whid is ",whid)
    #get current on-way package id
    sql = "SELECT trackingnum FROM users_package WHERE whid = %s AND status!='out for deliver' AND status!='delivered';"
    cursor.execute(sql,[whid])
    res = cursor.fetchall()
    if res:
        return res
    else:
        print("Cannot get the correct pacakgeid!")
        return -1

def getXY(db,packageid):
    cursor = db.cursor()
    sql = "SELECT x,y FROM users_package WHERE trackingnum=%s;"
    cursor.execute(sql, [packageid])
    res = cursor.fetchall()
    if res:
        return res[0]
    else:
        print("no such packageid")
        return None

##user##
def validateUserName(db, name):
    cursor = db.cursor()
    sql = "SELECT * FROM auth_user WHERE username=%s;"
    cursor.execute(sql, (name,))
    res = cursor.fetchall()
    if res:
        return True
    else:
        return False










'''
if __name__ == '__main__':
    conn=connectDB()
    createTableTruck(conn)
'''
