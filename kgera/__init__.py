from django import get_version
import pymysql

VERSION = (1, 0, 0, "final", 0)

__version__ = get_version(VERSION)

pymysql.install_as_MySQLdb()
