#!/usr/bin/env python

import logging
import random
import uuid
import sys
import pyrfc3339
import string
import datetime


def generate(type, invalid=False):
    return globals()['_generate_' + type.lower()](invalid=invalid)


def _generate_urn(invalid=False):
    if invalid:
        logging.debug('Generating invalid URN')
        return _random_string_generator()
    else:
        logging.debug('Generating URN')
        return 'urn:publicid:IDN+this_sa+project+myproject' + str(
            random.randint(0, sys.maxint))


def _generate_url(invalid=False):
    if invalid:
        return ''
    else:
        logging.debug('Generating URL')
        return 'https://'+_generate_string(length=5)+'.org:8008'


def _generate_uid(invalid=False):
    if invalid:
        return _random_string_generator()
    else:
        logging.debug('Generating UID')
        return str(uuid.uuid4())


def _generate_string(length=19, invalid=False):
    if invalid:
        logging.debug('Generating invalid string')
        # logging.error('Cannot generate invalid string due to UTF-8 restrictions in Python.')
        return ''
    else:
        logging.debug('Generating string')
        return _random_string_generator(length)


def _generate_integer(invalid=False):
    if invalid:
        logging.debug('Generating invalid integer')
        return _random_string_generator()
    else:
        logging.debug('Generating integer')
        return random.randint(0, sys.maxint)


def _generate_datetime(invalid=False):
    if invalid:
        logging.debug('Generating invalid datetime object')
        return _random_string_generator()
    else:
        logging.debug('Generating datetime object')
        _generate_datetime.counter += 1
        return str(pyrfc3339.generator.generate(datetime.datetime.now()+datetime.timedelta(days=10+_generate_datetime.counter),
                                                accept_naive=True))
_generate_datetime.counter = 0

def _generate_email(length=19, invalid=False):
    if invalid:
        logging.debug('Generating invalid email address')
        email = _random_string_generator(length)
    else:
        logging.debug('Generating email address')
        length = int(length / 2) - 5
        email = _random_string_generator(length) + '@' + \
            _random_string_generator(length) + '.' + \
            _random_string_generator(length=3)
    return email


def _generate_key(invalid=False):
    if invalid:
        logging.debug('Generating invalid key')
        return ''
    else:
        logging.debug('Generating key')
        return 'ssh-rsa '+_random_string_generator(length=372)


def _generate_username(invalid=False):
    if invalid:
        logging.debug('Generating invalid username')
        return ''
    else:
        logging.debug('Generating username')
        return _random_string_generator(length=8)


def _generate_cert(invalid=False):
    if invalid:
        logging.debug('Generating invalid certificate')
        return ''
    else:
        logging.debug('Generating certificate')
        return ''


def _generate_list(invalid=False):
    if invalid:
        logging.debug('Generating invalid list')
        return
    else:
        logging.debug('Generating list')
        return ''


def _generate_boolean(invalid=False):
    if invalid:
        logging.debug('Generating invalid boolean')
        return _random_string_generator()
    else:
        logging.debug('Generating boolean')
        return random.choice([True, False])


def _random_string_generator(length=19, invalid=False):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))
