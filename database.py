from peewee import IntegerField, SqliteDatabase, Model, IntegrityError, CharField, FloatField

# База данных пользователей
db_users_dtp = SqliteDatabase('users_eyewitness.db')

# База данных местоположения ДТП
db_location = SqliteDatabase('dtp_location.db')

# База данных доп. сообщений очевидцев
db_submessage = SqliteDatabase('message.db')


class BaseModelMessage(Model):
    """
    Базовый класс для модели местоположения доп. сообщений очевидцев
    """

    class Meta:
        database = db_submessage


class SubMessage(BaseModelMessage):
    """
    Модель доп. сообщений пользователей с подробностями о ДТП
    """
    id = IntegerField(primary_key=True)
    message = CharField(null=True)


class BaseModelLocation(Model):
    """
    Базовый класс для модели местоположения ДТП
    """

    class Meta:
        database = db_location


class Location(BaseModelLocation):
    """
    Модель местоположения
    """
    id = IntegerField(primary_key=True)
    address = CharField(null=True)
    latitude = FloatField()
    longitude = FloatField()


class BaseModelUsers(Model):
    """
    Базовый класс для модели пользователей
    """

    class Meta:
        database = db_users_dtp


class Users(BaseModelUsers):
    """
    Модель пользователей
    """
    phone_number = CharField()
    first_name = CharField()
    last_name = CharField(null=True)
    username = CharField()
    status = CharField(null=True)
    registration_data = CharField()
    user_id = IntegerField(primary_key=True)

