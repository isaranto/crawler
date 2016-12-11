# Crawler
An example of crawling data from a forum. The data are being "cleaned" using BeautifulSoup4 and are upload into a MySQL database using the peewee ORM.
The file "db-parameters.json" is needed in order to be able to initialize the database driver. You can just create a json file with the following:

{
   "host" : ip-address,
   "user" : db_user,
   "passwd" : passoword,
   "db" : db_name
}
