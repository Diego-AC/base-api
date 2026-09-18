try:
    from app import runserver
    app = runserver()
except Exception as exc:
    import sys
    import traceback

    sys.stderr.write("Failed to build Flask app: %s\n" % exc)
    traceback.print_exc()
    raise
