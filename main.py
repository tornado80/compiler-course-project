import sys
from src.compiler import compile_


compile_(sys.argv[1], ".")
