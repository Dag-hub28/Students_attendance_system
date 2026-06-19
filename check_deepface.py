import deepface
import pathlib
import sys
print('python', sys.executable)
print('deepface file', deepface.__file__)
print('deepface pkgdir', pathlib.Path(deepface.__file__).parent)
path = pathlib.Path(deepface.__file__)
data = path.read_bytes()
print('first bytes', data[:200])
print('null count', data.count(b'\x00'))
