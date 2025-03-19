import json
import re
import pandas as pd
import os
from util import docProcessing

# Initialize the docProcessing object
d = docProcessing()

print(d.pdfConversion("/mnt/d/fit3164/patent-analyser-fyp/120_file/20220031531.pdf"))