import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from util.log import logger

DEBUG = (os.getenv("DEBUG") == "True")
DATA_DIR = "{}/.economy_dog".format(os.environ['HOME'])
if DEBUG:
    DATA_DIR = "{}/.economy_dog_test".format(os.environ['HOME'])
# os.system("mkdir -p {}".format(DATA_DIR))
logger.info(f"work dir is: {DATA_DIR}")

sqlite_url = 'sqlite:///{}/dictionary.db'.format(DATA_DIR)
# engine = create_engine(sqlite_url, echo=DEBUG)
engine = create_engine(sqlite_url)
Session = sessionmaker(bind=engine)
# print(sqlite_url)
