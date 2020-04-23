import psycopg2
from database import *


if __name__ == '__main__':
    db=connectDB()
    #getWhid(db,1)
    print("get pckid:")
    print(getPackageIDFromTruckid(db,1))
    print("get whid:")
    print(getWhid(db,1))
    print("find idel truck:")
    print(findIdleTruck(db))
    print("add new package:")
    addPackage(db,"socks",123456,2,"zeyu",10,10)
    updatePackageStatus(db,"delivering","123456")

    print(validateUserName(db, 'admin1'))




