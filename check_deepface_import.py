try:
    from deepface import DeepFace
    print('DeepFace imported', DeepFace)
except Exception as e:
    import traceback
    traceback.print_exc()
