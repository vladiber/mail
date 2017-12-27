from datetime import datetime
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text , Search ,Nested
from elasticsearch_dsl.connections import connections

class Mail(DocType):
    mail_from = Text()
    attachments = Keyword()
    mail_to = Text()
    tags = Keyword()
    sent_day = Date()
    att_count = Integer()
    virus = Keyword()
    id = Text()
    
    class Meta:
        index = 'mail'

    def save(self, ** kwargs):
        return super(Mail, self).save(** kwargs)
    
    def add_tag(self, tag):
        self.tags.append(
          {'tags': tag})
    
def SearchES(mid):
    connections.create_connection(hosts=['localhost'])
    
    s = Search(index="mail") \
    .query("match", id=mid) 
    response = s.execute()

    return response
def GetMail(mid):
    connections.create_connection(hosts=['localhost'])
    mail = Mail.get(id=mid)
    return mail

def UpdateAtts(q,mid):
    connections.create_connection(hosts=['localhost'])
    mail = Mail.get(id=mid)
    if not mail.attachments:
        mail.attachments = q
    else:
        mail.attachments.append(q)
    mail.save()


def UpdateTags(status,mid):
    connections.create_connection(hosts=['localhost'])
    mail = Mail.get(id=mid)
    if not mail.tags:
        mail.tags = []
    mail.tags.append(status)
    mail.save()

def UpdateVirus(result,mid):
    connections.create_connection(hosts=['localhost'])
    mail = Mail.get(id=mid)
    mail.virus = result
    mail.save()
    
def WriteES(mfrom,mto,mid,an):
    connections.create_connection(hosts=['localhost'])
    # create the mappings in elasticsearch
    #Mail.init()
    mail = Mail(mail_from=mfrom,mail_to=mto,att_count=an)
    mail.meta.id = mid
    mail.sent_day = datetime.now()
    a = mail.save()

