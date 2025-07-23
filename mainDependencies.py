# import des librairies pour le main

from pycatia import catia
from pycatia.enumeration.enumeration_types import cat_work_mode_type
from pycatia.product_structure_interfaces.product import Product
from pycatia.product_structure_interfaces.product_document import ProductDocument
from pycatia.space_analyses_interfaces.inertia import Inertia
from pycatia.part_interfaces.rotate import Rotate
import numpy as np

##########################################################

import pygame
from pygame.locals import *

##########################################################
# insert syspath to project folder so examples can be run.
# for development purposes.
import os
import sys

sys.path.insert(0, os.path.abspath("..\\pycatia"))
##########################################################

import win32con
import win32gui

##########################################################

from scipy.spatial import ConvexHull

##########################################################