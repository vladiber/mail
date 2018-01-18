import MySQLdb
class DbPass:
    db = MySQLdb.connect(host="192.168.204.131",user="mail",passwd="mail",db="mail")
    cur = db.cursor()
    def insert_pass(self,f,to,p):
        
        insert = ("INSERT into pass_store (rcpt_from,rcpt_to,pass) values (%s,%s,%s)")
        data = (f,to,p)
        self.cur.execute(insert,data)
        res = self.db.commit()
        print res
    def retreive_pass(self,f,to):
        select = ("select pass from pass_store where rcpt_from = %s and rcpt_to = %s")
        data = (f,to)
        self.cur.execute(select,data)
        for (passw) in self.cur:
            #print passw[0]
            return passw[0]
        
#DbPass().insert_pass('ff','tt','pp')
#a = DbPass()
#a.retreive_pass('ff','tt')
