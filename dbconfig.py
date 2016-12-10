from peewee import *
import json


def init_db():
    with open('db-parameters.json', 'r') as data_file:
        params = json.load(data_file)
    my_host = params.get(u'host')
    my_user = params.get(u'user')
    my_passwd = params.get(u'passwd')
    my_db = params.get(u'db')
    db = MySQLDatabase(host=my_host,
                                  user=my_user,
                                  passwd=my_passwd,
                                  database=my_db)
    return db


class BaseModel(Model):
    class Meta:
        database = init_db()


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

