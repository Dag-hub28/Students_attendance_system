import pathlib
p=pathlib.Path('attendance_system_deepface.py')
b=p.read_bytes()
print(repr(b[:200]))
print('nulls', b.count(b'\x00'))
