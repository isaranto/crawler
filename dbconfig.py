from peewee import *
import json

class database_driver:
    def __init__(self):
        with open('db-parameters.json', 'r') as data_file:
            params = json.load(data_file)
        my_host = params.get(u'host')
        my_user = params.get(u'user')
        my_passwd = params.get(u'passwd')
        my_db = params.get(u'db')
        self.db = MySQLDatabase(host=my_host,
                                      user=my_user,
                                      passwd=my_passwd,
                                      database=my_db)



class BaseModel(Model):
    class Meta:
        database = database_driver().db


class users(BaseModel):
    username = CharField()
    id = IntegerField(primary_key=True)


class articles(BaseModel):
    title = CharField()
    text = CharField()
    id = BigIntegerField(primary_key=True)
    user_id = ForeignKeyField(users,  db_column='user_id',related_name='articles')


class comments(BaseModel):
    time = DateTimeField()
    user_id = ForeignKeyField(users, db_column='user_id', related_name='users')
    article_id = ForeignKeyField(articles,db_column='article_id', related_name='articles')
    text = TextField()
    id = BigIntegerField(primary_key=True)
    votes = IntegerField()

class videos(BaseModel):
    comment_id = ForeignKeyField(comments,  db_column='comment_id', related_name='comments')
    url = CharField()
    token = CharField()
    article_id = ForeignKeyField(articles,  db_column='article_id')

