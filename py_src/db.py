from peewee import *

import config

mysql_db = MySQLDatabase(
    config.DB_NAME,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=3306
)


class PostMeta(Model):
    meta_id = PrimaryKeyField()
    post_id = IntegerField()
    meta_key = TextField()
    meta_value = TextField()

    class Meta:
        database = mysql_db
        table_name = config.DB_TABLE_NAME


def add_post_meta(post_id, meta_key, meta_value):
    try:
        pm = PostMeta.get(PostMeta.post_id == post_id, PostMeta.meta_key == meta_key)
        pm.meta_value = meta_value
        return pm.save()
    except DoesNotExist:
        return PostMeta(post_id=post_id, meta_key=meta_key, meta_value=meta_value).save()
