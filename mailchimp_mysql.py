# --*-- coding: UTF-8 --*--

import sys
import logging

import sqlsoup
import requests
import json
from datetime import datetime

from mailchimp3 import MailChimp

from config import init_config


logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s] %(message)s', 
    level=logging.INFO, filename='mylog.log'
)

# block with constants
PASSWORD = sys.argv[1] # read this secret constant from stdin

#default user status in mailchimp
MAILCHIPM_STATUS = "subscribed"

#flags which are describe type of users and its active status
SUPERUSER_TRUE = 1
STAFF_TRUE = 1
ACTIVE_TRUE = 1

#constant with necessary amount of users
AMOUNT_OF_USERS = 1500


def get_data_from_db(user, password, host, port, dbname):
    sql_dialect = u"mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}".format(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname
    )
    db = sqlsoup.SQLSoup(sql_dialect)
    return db.auth_user.all()


def filter_data(data):
    list_with_users = []
    for user in data:
        if not(user.is_superuser == SUPERUSER_TRUE or user.is_staff == STAFF_TRUE):
            if user.is_active == ACTIVE_TRUE:
                list_with_users.append({
                "email_address": "{}".format(user.email),
                "status": MAILCHIPM_STATUS,
                "merge_fields": {
                    "FNAME": "{}".format(user.username),
                    "LNAME": ""
                    }
                })
    return list_with_users[:AMOUNT_OF_USERS]


def avoid_repetable_data(mailchimp_list, db_list):
    _list = []
    for item in db_list:
        if item['email_address'] not in mailchimp_list:
            _list.append(item)
    return _list


def main():
    #get dict with configurations from 'dev.yaml'
    config = init_config()
    logging.info(u'Считало конфигурции')

    #mysql configurations
    mysql_config = config['mysql']
    logging.info(u'Распарсило конфиги и создался словарь с конфигурциями для mysql.')

    #mailchimp configurations
    mailchimp_config = config['mailchimp']
    logging.info(u'Распарсило конфиги и создался словарь с конфигурциями для mailchimp.')

    #get all users from mysqlDB 'edxapp'
    data_from_db = get_data_from_db(
        user=mysql_config['user'],
        password=PASSWORD,
        host=mysql_config['host'],
        port=mysql_config['port'],
        dbname=mysql_config['dbname']
    )
    logging.info(
        u'Достало из базы {dbname} кол-во записей {amount}'.format(
            dbname=mysql_config['dbname'],
            amount=len(data_from_db)
        )
    )

    #create mailchimp client
    client = MailChimp(
        mailchimp_config['username'],
        mailchimp_config['app_key']
    )
    logging.info(u'Создалcя mailchimp client.')

    list_id = mailchimp_config['lists_ids'][0]
    req_before = client.lists.members.all(list_id, count=2000, offset=0)
    users_exist = req_before['total_items']
    logging.info(
        u'Получено данные с mailchimp. Всего в списке с id={id} уже есть {amount} записей.'.format(
            id=list_id,
            amount=users_exist
        )
    )

    #create lists with email of users which already exist in mailchimp.
    already_exists_users_list = []
    if users_exist != 0:
        for i in req_before['members']:
            already_exists_users_list.append(str(i["email_address"]))
        logging.info(
            u'Создалcя список с {amount} users уже залитых на mailchimp.'.format(
                amount=len(already_exists_users_list)
            )
        )

    needfull_list = avoid_repetable_data(
        already_exists_users_list,
        filter_data(data_from_db)
    )
    must_be_users_amount = len(needfull_list)

    #pull users to mailchimp
    for item in needfull_list:
        client.lists.members.create(list_id=list_id, data=item)

    #check sent data
    req_after = client.lists.members.all(list_id, count=2000, offset=0)
    logging.info(u'Должно было залиться {expected_amount} записей. Было залито: {actual_amount}'.format(
            expected_amount=must_be_users_amount,
            actual_amount=req_after['total_items'] - users_exist
        )
    )


if __name__ == '__main__':
    main()
