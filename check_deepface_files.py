import pathlib
root = pathlib.Path('myemv/Lib/site-packages/deepface')
print('root', root.exists(), root)
for p in sorted(root.rglob('*.py')):
    data = p.read_bytes()
    count = data.count(b'\x00')
    if count:
        print('NULLS', p, count)
        continue
    try:
        compile(data.decode('utf-8'), str(p), 'exec')
    except Exception as e:
        print('COMPILE FAIL', p, type(e).__name__, e)
