import psycopg2
from database import *


if __name__ == '__main__':
    db=connectDB()
    #getWhid(db,1)
    print("get pckid:")
    print(getPackageIDFromTruckid(db,0))
    print("get whid:")
    print(getWhid(db,1))
    print("find idel truck:")
    print(findIdleTruck(db))

    print(validateUserName(db, 'admin1'))

    print(getX(db,12345))



