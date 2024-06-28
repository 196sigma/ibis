import os
import shutil
from datetime import datetime, timedelta
import urllib
import zipfile
import matplotlib.pyplot as plt
import requests
import pandas as pd
from configs import FRD_USER_ID, FRD_DATA_DIR

ZIP_FILES_DIR = os.path.join(FRD_DATA_DIR, asset_type, "zips")

