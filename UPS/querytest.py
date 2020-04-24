import psycopg2
from database import *
from sendemail import *

def  makestr(x):
    string=""
    string+= x
    print(string)

if __name__ == '__main__':
    db=connectDB()
    #getWhid(db,1)
    '''
    print("get pckid:")
    print(getPackageIDFromTruckid(db,1))
    print("get whid:")
    print(getWhid(db,1))
    print("find idel truck:")
    print(findIdleTruck(db))

    print(validateUserName(db, 'admin1'))


    print(getXY(db,12345))'''
    #addPackage(db,"apple",123,2,"zeyu",12,12)
    #makestr(1)
    a=getEmailAddrFromPckid(db,12)
    if(a):
        print("exist")
        sendEmail(a)
    else:
        print("not exist")



