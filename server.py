import os.path
import datetime
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
from binascii import hexlify
import tornado.web
from tornado.options import define, options
import json

define("port", default=1104, help="run on the given port", type=int)
define("mysql_host", default="localhost:3306", help="database host")
define("mysql_database", default="tickets", help="database name")
define("mysql_user", default="manager", help="database user")
define("mysql_password", default="nice", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/signup/([^/]+)/([^/]+)/([^/]+)/([^/]+)", signup),
            (r"/login/([^/]+)/([^/]+)", login),
            (r"/logout/([^/]+)/([^/]+)", logout),
            (r"/sendticket/([^/]+)/([^/]+)/([^/]+)", sendticket),
            (r"/getticketcli/([^/]+)", getticketcli),
            (r"/closeticket/([^/]+)/([^/]+)", closeticket),
            (r"/getticketmod/([^/]+)", getticketmod),
            (r"/restoticketmod/([^/]+)/([^/]+)/([^/]+)", restoticketmod),
            (r"/changestatus/([^/]+)/([^/]+)/([^/]+)", changestatus),
            (r"/authcheck/([^/]+)/([^/]+)", authcheck),
            (r"/apicheck/([^/]+)", apicheck),

            (r"/signup", signup),
            (r"/login", login),
            (r"/logout", logout),
            (r"/sendticket", sendticket),
            (r"/getticketcli", getticketcli),
            (r"/closeticket", closeticket),
            (r"/getticketmod", getticketmod),
            (r"/restoticketmod", restoticketmod),
            (r"/changestatus", changestatus),
            (r"/authcheck", authcheck),
            (r"/apicheck", apicheck),
            (r".*", defaulthandler),
        ]
        settings = dict()
        super(Application, self).__init__(handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    def check_user(self,user):
        resuser = self.db.get("SELECT * from users where username = %s",user)
        if resuser:
            return True
        else :
            return False

    def check_api(self,api):
        resuser = self.db.get("SELECT * from users where api = %s", api)
        if resuser:
            return True
        else:
            return False
    def check_auth(self,username,password):
        resuser = self.db.get("SELECT * from users where username = %s and password = %s", username,password)
        if resuser:
            return True
        else:
            return False
    def check_admin(self,api):
        resuser = self.db.get("SELECT * from users where api = %s and isadmin = 'y'",api)
        if resuser:
            return True
        else:
            return False

class defaulthandler(BaseHandler):
    def get(self):
        output = {'code':'Wrong Command'}
        self.write(output)

    def post(self, *args, **kwargs):
        output = {'code':'Wrong Command'}
        self.write(output)


class signup(BaseHandler):
    def get(self,*args):
        if not self.check_user(args[0]):
            api_token = str(hexlify(os.urandom(16)))
            user_id = self.db.execute("INSERT INTO users (username, password, api, fname, lname, isadmin, ticketnums) "
                                     "values (%s,%s,%s,%s,%s,%s,%s) "
                                     , args[0],args[1],api_token,args[2],args[3],'n', 0)

            output = {'token': api_token,
                      'code': '200'}
            self.write(output)
        else:
            output = {'code': 'User Exist'}
            self.write(output)
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        fname = self.get_argument('firstname')
        lname = self.get_argument('lastname')
        if not self.check_user(username):
            api_token = str(hexlify(os.urandom(16)))
            user_id = self.db.execute("INSERT INTO users (username, password, api ,fname, lname, isadmin, ticketnums) "
                                     "values (%s,%s,%s,%s,%s,%s,%s) "
                                     , username,password,api_token, fname,lname,'n',0)

            output = {'token' : api_token,
                      'code' : '200'}
            self.write(output)
        else:
            output = {'code': 'User Exist'}
            self.write(output)

class login(BaseHandler):
    def get(self, *args):
        if self.check_auth(args[0], args[1]):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("UPDATE users set api = %s where username = %s and password = %s",api_token , args[0], args[1])
            api_token = self.db.get("SELECT api from users where username = %s", args[0])
            output ={"message": "Logged in Successfully",
                "code": "200",
                "token": api_token['api']}
            self.write(output)
        else:
            output ={"message": "Unsuccessfull!",
                        "code" : "401"}
            self.write(output)
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if self.check_auth(username, password):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("UPDATE users set api = %s where username = %s and password = %s",api_token , username, password)
            api_token = self.db.get("SELECT api from users where username = %s", username)
            output ={"message": "Logged in Successfully",
                "code": "200",
                "token": api_token['api']}
            self.write(output)
        else:
            output ={"message": "Unsuccessfull!",
                        "code" : "401"}

class logout(BaseHandler):
    def get(self, *args):
        if self.check_auth(args[0], args[1]):
            output = {"message": "Logged out Successfully",
                        "code" : "200"}
        else:
            output = {"message": "UnSuccessfully",
                        "code" : "401"}
        self.write(output)
    def post(self):
        username = self.get_arguments("username")
        password = self.get_arguments("password") 
        if self.check_auth(username, password):
            output = {"message": "Logged Out Successfully",
                "code": "200"}
        else:
            output = {"message": "UnSuccessfully",
                        "code" : "401"}
        self.write(output)

class sendticket(BaseHandler):
    def post(self):
        token = self.get_arguments("token")
        subject = self.get_arguments("subject")
        body = self.get_arguments("body")
        if self.check_api(token):
            now = datetime.datetime.now()
            user_id = self.db.get("SELECT staff_number from users where api = %s", token)
            tockensent = self.db.get("SELECT ticketnums from users where api = %s",token)
            admin_id = self.db.get("SELECT staff_number from users where isadmin = 'y'")
            ticketSend = self.db.execute("INSERT INTO tickets (sender, subject,body ,status, date , receiver) "
                                     "values (%s,%s,%s,%s,%s,%s) "
                                     , user_id['staff_number'] , subject,body,'in progress', now, admin_id['staff_number'])
            self.db.execute("UPDATE users set ticketnums = ticketnums + %s where staff_number = %s",1,user_id['staff_number'])
            output = {"message": "Ticket Sent Successfully",
                    "id": admin_id['staff_number'],
                    "code": "200"}
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
        self.write(output)
    def get(self,*args):
        if self.check_api(args[0]):
            now = datetime.datetime.now()
            user_id = self.db.get("SELECT staff_number from users where api = %s", args[0])
            tockensent = self.db.get("SELECT ticketnums from users where api = %s",args[0])
            admin_id = self.db.get("SELECT staff_number from users where isadmin = 'y'")
            ticketSend = self.db.execute("INSERT INTO tickets (sender, subject,body ,status, date , receiver) "
                                     "values (%s,%s,%s,%s,%s,%s) "
                                     , user_id['staff_number'] , args[1],args[2],'in progress', now, admin_id['staff_number'])
            self.db.execute("UPDATE users set ticketnums = ticketnums + %s where staff_number = %s",1,user_id['staff_number'])
            output = {"message": "Ticket Sent Successfully",
                    "id": admin_id['staff_number'],
                    "code": "200"}
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
        self.write(output)

class getticketcli(BaseHandler):
    def post(self):
        token = self.get_arguments("token")
        if self.check_api(token):
            user_id = self.db.get("SELECT staff_number from users where api = %s", token)
            myTickets = self.db.query("SELECT * from tickets where sender = %s or receiver = %s", user_id['staff_number'] , user_id['staff_number'])
            ticketnums = self.db.get("SELECT COUNT(*) from tickets where sender = %s or receiver = %s", user_id['staff_number'] , user_id['staff_number'])
            #print(str(myTickets))
            output = {"tickets": "There Are -"+str(ticketnums['COUNT(*)'])+"- Tickets",
                    "code": "200",
                    "blocks": {}
                    }
            for i in range(0,ticketnums['COUNT(*)']):
                output2 = {"block "+str(i):{
                            "subject": myTickets[i]['subject'],
                            "body": myTickets[i]['body'],
                            "status": myTickets[i]['status'],
                            "idd": myTickets[i]['staff_number'],
                            "date": myTickets[i]['date']
                            }
                        }
                output['blocks'].update(output2)
            self.write(output)
                
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
            self.write(output)
    def get(self, *args):
        if self.check_api(args[0]):
            user_id = self.db.get("SELECT staff_number from users where api = %s", args[0])
            myTickets = self.db.query("SELECT * from tickets where sender = %s or receiver = %s", user_id['staff_number'], user_id['staff_number'])
            ticketnums = self.db.get("SELECT COUNT(*) from tickets where sender = %s or receiver = %s", user_id['staff_number'] , user_id['staff_number'])
            output = {"tickets": "There Are -"+str(ticketnums['COUNT(*)'])+"- Tickets",
                    "code": "200",
                    "blocks": {}
                    }
            for i in range(0,ticketnums['COUNT(*)']):
                output2 = {"block "+str(i):{
                            "subject": myTickets[i]['subject'],
                            "body": myTickets[i]['body'],
                            "status": myTickets[i]['status'],
                            "idd": myTickets[i]['staff_number'],
                            "date": myTickets[i]['date']
                            }
                        }
                output['blocks'].update(output2)
            self.write(output)
                
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
            self.write(output)


class closeticket(BaseHandler):
    def post(self):
        token = self.get_arguments("token")
        idd = self.get_arguments("id")
        if self.check_api(token):
            user_id = self.db.get("SELECT staff_number from users where api = %s", token)
            res = self.db.get("SELECT * from tickets where sender = %s and staff_number = %s",user_id['staff_number'], idd[0])
            if res:
                res = self.db.execute("UPDATE tickets set status = %s where staff_number = %s and sender = %s","close",idd[0],user_id['staff_number'])
                output = {"message": "Ticket With idd -"+ idd[0]+"- Closed Successfully",
                    "code": "200"}
            else:
                output = {"message": "Ticket With idd -"+idd[0]+"- is not exist!",
                    "code": "401"}
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
        self.write(output)
    def get(self, *args):
        if self.check_api(args[0]):
            user_id = self.db.get("SELECT staff_number from users where api = %s", args[0])
            res = self.db.get("SELECT * from tickets where sender = %s and staff_number = %s",user_id['staff_number'], args[1])
            if res:
                res = self.db.execute("UPDATE tickets set status = %s where staff_number = %s and sender = %s","close",args[1],user_id['staff_number'])
                output = {"message": "Ticket With idd -"+ args[1]+"- Closed Successfully",
                    "code": "200"}
            else:
                output = {"message": "Ticket With idd -"+args[1]+"- is not exist!",
                    "code": "401"}
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
        self.write(output)

class getticketmod(BaseHandler):
    def get(self , *args):
        if self.check_admin(args[0]):
            myTickets = self.db.query("SELECT * from tickets")
            ticketnums = self.db.get("SELECT COUNT(*) FROM tickets")
            print(ticketnums)
            #print(str(myTickets))
            output = {"tickets": "There Are -"+str(ticketnums['COUNT(*)'])+"- Tickets",
                    "code": "200",
                    "blocks": {}
                    }
            for i in range(0,ticketnums['COUNT(*)']):
                output2 = {"block "+str(i):{
                            "subject": myTickets[i]['subject'],
                            "body": myTickets[i]['body'],
                            "status": myTickets[i]['status'],
                            "idd": myTickets[i]['staff_number'],
                            "date": myTickets[i]['date']
                            }
                        }
                output['blocks'].update(output2)
            self.write(output)
                
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}
    def post(self):
        token = self.get_argument("token")
        if self.check_admin(token):
            myTickets = self.db.query("SELECT * from tickets")
            ticketnums = self.db.get("SELECT COUNT(*) FROM tickets")
            #print(str(myTickets))
            output = {"tickets": "There Are -"+str(ticketnums['COUNT(*)'])+"- Ticket",
                    "code": "200",
                    "blocks": {}
                    }
            for i in range(0,ticketnums['COUNT(*)']):
                output2 = {"block "+str(i):{
                            "subject": myTickets[i]['subject'],
                            "body": myTickets[i]['body'],
                            "status": myTickets[i]['status'],
                            "idd": myTickets[i]['staff_number'],
                            "date": myTickets[i]['date']
                            }
                        }
                output['blocks'].update(output2)
            self.write(output)
                
        else:
            output = {"message": "Unsuccessfull (api_error)",
                    "code": "401"}

class restoticketmod(BaseHandler):
    def post(self):
        token = self.get_argument("token")
        idd = self.get_argument("id")
        body = self.get_argument("body")
        if self.check_admin(token):
            now = datetime.datetime.now()
            user_id = self.db.get("SELECT staff_number from users where api = %s", token)
            ticket = self.db.get("SELECT * from tickets where staff_number = %s",idd[0])
            if ticket:
                ticketSend = self.db.execute("INSERT INTO tickets (sender, subject,body ,status, date, receiver) "
                                        "values (%s,%s,%s,%s,%s,%s) "
                                        , user_id['staff_number'] , ticket['subject'],body,'in progress', now,ticket['sender'])
                self.db.execute("UPDATE users set ticketnums = ticketnums + %s where staff_number = %s",1,user_id['staff_number'])
                self.db.execute("UPDATE tickets set status = %s where staff_number = %s","close",idd[0])
                output = {"message": "Response to Ticket With id -"+ str(idd) +"- Sent Successfully",
                        "code": "200"}
            else:
                output = {"message": "Unsuccessfull! (id dose not exist!)",
                    "code": "401"}

        else:
            output = {"message": "Unsuccessfull! (permission denied)",
                    "code": "401"}
        self.write(output)
    def get(self,*args):
        if self.check_admin(args[0]):
            now = datetime.datetime.now()
            user_id = self.db.get("SELECT staff_number from users where api = %s", args[0])
            ticket = self.db.get("SELECT * from tickets where staff_number = %s",args[1])
            if ticket:
                ticketSend = self.db.execute("INSERT INTO tickets (sender, subject,body ,status, date, receiver) "
                                        "values (%s,%s,%s,%s,%s,%s) "
                                        , user_id['staff_number'] , ticket['subject'],args[2],'in progress', now,ticket['sender'])
                self.db.execute("UPDATE users set ticketnums = ticketnums + %s where staff_number = %s",1,user_id['staff_number'])
                self.db.execute("UPDATE tickets set status = %s where staff_number = %s","close",args[1])
                output = {"message": "Response to Ticket With id -"+ str(args[1]) +"- Sent Successfully",
                        "code": "200"}
            else:
                output = {"message": "Unsuccessfull! (id dose not exist!)",
                    "code": "401"}
        else:
            output = {"message": "Unsuccessfull! (permission denied)",
                    "code": "401"}
        self.write(output)
            
class changestatus(BaseHandler):
    def post(self):
        token = self.get_argument("token")
        idd = self.get_argument("id")
        status = self.get_argument("status")
        if self.check_admin(token):
            ticketID = self.db.get("SELECT * from tickets where staff_number = %s",idd[0])
            if ticketID:
                self.db.execute("UPDATE tickets set status = %s where staff_number = %s",status,idd[0])
                output = {"message": "Status Ticket With id -"+ idd[0]+"- Changed Successfully",
                            "code": "200"}
            else:
                output = {"message": "Unsuccessfull! (id dose not exist!)",
                    "code": "401"}
        else:
            output = {"message": "Unsuccessfull! (permission denied)",
                        "code": "401"}
        self.write(output)
    def get(self, *args):
        if self.check_admin(args[0]):
            ticketID = self.db.get("SELECT * from tickets where staff_number = %s",args[1])
            if ticketID:
                self.db.execute("UPDATE tickets set status = %s where staff_number = %s",args[2],args[1])
                output = {"message": "Status Ticket With id -"+ args[1]+"- Changed Successfully",
                            "code": "200"}
            else:
                output = {"message": "Unsuccessfull! (id dose not exist!)",
                    "code": "401"}
        else:
            output = {"message": "Unsuccessfull! (permission denied)",
                        "code": "401"}
        self.write(output)





class help(BaseHandler):
    def get(self, *args, **kwargs):
       self.write("Tornado is Runnig")

class authcheck(BaseHandler):
    def get(self, *args, **kwargs):
        if self.check_auth(args[0],args[1]):
            user = self.db.get("SELECT * from users where username = %s and password = %s", args[0], args[1])
            output = {'code' : '200',
                      'api' : user.api,
                      'username' : user.username}
            self.write(output)
        else:
            output = {'code': '401'}
            self.write(output)

    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if self.check_auth(username,password):
            user = self.db.get("SELECT * from users where username = %s and password = %s", username, password)
            output = {'code': '200',
                      'api': user.api,
                      'username': user.username}
            self.write(output)
        else:
            output = {'code': '401'}
            self.write(output)

class apicheck(BaseHandler):
    def get(self, *args, **kwargs):
        if self.check_api(args[0]):
            user = self.db.get("SELECT * from users where api = %s", args[0])
            output = {'code': '200',
                      'api': user.api,
                      'username': user.username}
            self.write(output)
        else:
            output = {'code': '401'}
            self.write(output)

    def post(self, *args, **kwargs):
        api = self.get_argument('api')
        if self.check_api(api):
            user = self.db.get("SELECT * from users where api = %s", api)
            output = {'code': '200',
                      'api': user.api,
                      'username': user.username}
            self.write(output)
        else:
            output = {'code': '401'}
            self.write(output)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
