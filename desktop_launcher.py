"""SparkTwin desktop entry point for PyInstaller and source runs."""
from __future__ import annotations
import sys, threading, webbrowser
from sparktwin.packaged import root


def main():
    if '--self-test' in sys.argv:
        base=root()
        assert (base/'sparktwin'/'web'/'index.html').is_file(), 'Missing interface'
        assert (base/'sparktwin'/'web'/'app.js').is_file(), 'Missing browser controller'
        from sparktwin.model import assess, DEFAULT
        assert assess(DEFAULT)['physical_gib'] > 100
        print('SparkTwin packaged source integrity: OK')
        return
    from sparktwin.app import Controller
    app=Controller().start()
    server_thread=threading.Thread(target=app.server.serve_forever,daemon=True)
    server_thread.start()
    try:
        try:
            import webview
            webview.create_window('SparkTwin · AI Capacity Intelligence',app.url,width=1440,height=920,min_size=(860,600),background_color='#08121f')
            webview.start()
        except (ImportError,RuntimeError,OSError):
            # A functioning browser is preferable to a failed optional native toolkit.
            webbrowser.open(app.url)
            print('Desktop webview unavailable. Open '+app.url,flush=True)
            server_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        if app.server:
            app.server.shutdown()
            server_thread.join(timeout=5)
            app.close()


if __name__=='__main__': main()
