import pymysql
import time, datetime
from mail_utility import mail


def connectit():
    conn = pymysql.connect(host='localhost',port=3306,user='admin',passwd='Admin@123',db='suscrib')
    cursor = conn.cursor()
    return cursor, conn

cursor, conn = connectit()

def get_client(id):
    columns = {
        "id": 0,
        "Name": 1,
        "CusId": 2,
        "isArchived": 6
    }
    query = "select * from clients_client where id = %s"
    cursor.execute(query,(id))
    client = cursor.fetchall()
    if len(client) == 1:
        if not client[0][columns["isArchived"]]:
            return True
        else:
            return False
    return None

def get_user(id):
    columns = {
        "id": 0,
        "username": 4,
        "email": 7,
        "is_active": 9
    }
    query = "select * from auth_user where id = %s"
    cursor.execute(query,(id))
    users = cursor.fetchall()
    if len(users) == 1:
        user = users[0]
        if user[columns["is_active"]]:
            # print(user[columns["username"]])
            return user[columns["username"]], user[columns["email"]]
    return None

def get_users_profile(customerId):
    columns = {
        "user_id": 0,
        "firstLogin": 1,
        "reset": 2,
        "key": 3,
        "cid_id": 4
    }
    query = "select * from users_userprofile where cid_id = %s"
    cursor.execute(query,(customerId))
    user_profile = cursor.fetchall()
    users = []
    if len(user_profile) > 0:
        for user in user_profile:
            try:
                username, email = get_user(user[columns["user_id"]])
                users.append({"username": username, "email": email})
            except:
                pass
        return users
    return None

def get_hci(id):
    columns = {
        "id": 0,
        "MachineID": 1,
        "Customer_id": 2,
        "isArchived": 3
    }
    query = "select * from clients_hci where id = %s"
    cursor.execute(query,(id))
    hci = cursor.fetchall()
    if len(hci) == 1:
        hciId = hci[0][columns["MachineID"]]
        customerId = hci[0][columns["Customer_id"]]
        if not hci[0][columns["isArchived"]]:
            return hciId, customerId
    return None

def get_app(id):
    columns = {
        "id": 0,
        "ApplicationName": 1,
        "isArchived": 2
    }
    query = "select * from licence_application where id = %s"
    cursor.execute(query,(id))
    app = cursor.fetchall()
    if len(app) == 1:
        appName = app[0][columns["ApplicationName"]]
        if not app[0][columns["isArchived"]]:
            return appName
    return None

def licenceNotify(query, columns):
    print("----------", query["purpose"], "-----------")
    for expireD in query["limits"]:
        args = (expireD)
        print(args)
        cursor.execute(query["query"], args)
        listExpireInOneD = cursor.fetchall()
        for item in listExpireInOneD:
            print(item[columns['App_id']])
            grace = (item[columns["graceExpiryDate"]] - item[columns["graceIssueDate"]]).days
            appName = get_app(item[columns['App_id']])
            print(appName)
            if appName:
                hciId, customerId = get_hci(item[columns['App_id']])
                if get_client(customerId):
                    users = get_users_profile(customerId)
                    print(users)
                    for user in users:
                        print(
                            "Email Id:{email}, username:{username}, purpose:{purpose}, hciId:{hciId}, app:{app}, grace:{grace}, start:{start}, end:{end}"
                            .format(email=user["email"], username=user["username"], purpose=query["purpose"],
                                    hciId=hciId, app=appName, grace=grace, start=item[columns["issueDate"]],
                                    end=item[columns["expiryDate"]]))
                        check = mail(to_address=user["email"], username=user["username"],purpose=query["purpose"], hciId=hciId, app=appName, grace=grace, start=item[columns["issueDate"]], end=item[columns["expiryDate"]])
                        print(check)

def trialNotify(query, columns):
    print("----------", query["purpose"], "-----------")
    for expireD in query["limits"]:
        args = (expireD)
        print(args)
        cursor.execute(query["query"], args)
        listExpireInOneD = cursor.fetchall()
        for item in listExpireInOneD:
            print(item[columns['App_id']])
            appName = get_app(item[columns['App_id']])
            print(appName)
            if appName:
                hciId, customerId = get_hci(item[columns['App_id']])
                if get_client(customerId):
                    users = get_users_profile(customerId)
                    print(users)
                    for user in users:
                        print(
                            "Email Id:{email}, username:{username}, purpose:{purpose}, hciId:{hciId}, app:{app}, start:{start}, end:{end}"
                            .format(email=user["email"], username=user["username"], purpose=query["purpose"],
                                    hciId=hciId, app=appName, start=item[columns["graceIssueDate"]],
                                    end=item[columns["graceExpiryDate"]]))
                        check = mail(to_address=user["email"], username=user["username"],purpose=query["purpose"], hciId=hciId, app=appName, start=item[columns["graceIssueDate"]]
                                     , end=item[columns["graceExpiryDate"]])
                        print(check)

def supportNotify(query, columns):
    print("----------", query["purpose"], "-----------")
    for expireD in query["limits"]:
        args = (expireD)
        print(args)
        cursor.execute(query["query"], args)
        listExpireInOneD = cursor.fetchall()
        for item in listExpireInOneD:
            print(item[columns['App_id']])
            days = abs((item[columns['expiryDate']] - item[columns["graceIssueDate"]]).days)
            print(days)
            if days == 1:
                appName = get_app(item[columns['App_id']])
                print(appName)
                if appName:
                    hciId, customerId = get_hci(item[columns['App_id']])
                    if get_client(customerId):
                        users = get_users_profile(customerId)
                        print(users)
                        for user in users:
                            print(
                                "Email Id:{email}, username:{username}, purpose:{purpose}, hciId:{hciId}, app:{app}, start:{start}, end:{end}"
                                .format(email=user["email"], username=user["username"], purpose=query["purpose"],
                                        hciId=hciId, app=appName, start=item[columns["graceIssueDate"]],
                                        end=item[columns["graceExpiryDate"]]))
                            # check = mail(to_address=user["email"], username=user["username"],purpose=query["purpose"], hciId=hciId, app=appName, start=item[columns["graceIssueDate"]]
                            #              , end=item[columns["graceExpiryDate"]])
                            # print(check)

def main():
    """
        issueDate expiryDate graceIssueDate graceExpiryDate trial
    :return:
    """
    columns = {
        "id": 0,
        "issueDate": 1,
        "expiryDate": 2,
        "graceIssueDate": 3,
        "graceExpiryDate": 4,
        "App_id": 5,
        "MachineID_id": 6,
        "OrderID_id": 7,
        "trial": 8,
        "isArchived": 9
    }
    expireToday = datetime.datetime.today().date()
    expireInOneD = datetime.datetime.today().date() + datetime.timedelta(days=1)
    expireInThreeD = datetime.datetime.today().date() + datetime.timedelta(days=3)
    expireInSevenD = datetime.datetime.today().date() + datetime.timedelta(days=7)
    # alerts = [expireInOneD, expireInThreeD, expireInSevenD]
    # query1 = "select * from licence_licence where expiryDate = %s"
    # query2 = "select * from licence_licence where trial=True and graceExpiryDate = %s"
    expireNotify = [
        {
            "query": "select * from licence_licence where expiryDate = %s",
            "limits": [expireInOneD, expireInThreeD, expireInSevenD],
            "purpose": "expireLicenceNotify",
            "kwargs": {

            }
        },
        {
            "query": "select * from licence_licence where trial=True and graceExpiryDate = %s",
            "limits": [expireInOneD, expireInThreeD, expireInSevenD],
            "purpose": "expireTrialNotify"
        },
        {
            "query": "select * from licence_licence where trial=False and graceExpiryDate = %s",
            "limits": [expireToday,],
            "purpose": "fullExpireSupportNotify"
        }
    ]
    # query = expireNotify[0]
    # licenceNotify(query, columns)
    # query = expireNotify[1]
    # trialNotify(query, columns)
    query = expireNotify[2]
    supportNotify(query, columns)

# if __name__ == "__main__":
main()