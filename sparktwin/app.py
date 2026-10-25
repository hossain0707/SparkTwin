"""Loopback-only web controller; no cloud calls or remotely installed agent."""
from __future__ import annotations
import argparse, json, os, secrets, threading, webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from . import __version__
from .model import DEFAULT, PROFILES, InvalidScenario, assess, recommend_variant
from .calibration import calibrate
from .store import Store
from .ssh import aliases, inspect
from .pdf import report_pdf
from .packaged import root as packaged_root

ROOT=packaged_root()
WEB=ROOT/"sparktwin"/"web"
MAX_BODY=512*1024


class Controller:
    def __init__(self, store=None):
        self.store=store or Store()
        self.token=secrets.token_urlsafe(32)
        self.server=None

    def start(self, port=0):
        c=self
        class Handler(BaseHTTPRequestHandler):
            protocol_version="HTTP/1.1"
            def log_message(self, fmt,*args):
                if os.environ.get("SPARKTWIN_DEBUG"): super().log_message(fmt,*args)

            def send(self,status,payload,content_type="application/json; charset=utf-8",attachment=None):
                if isinstance(payload,(dict,list)): payload=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode()
                elif isinstance(payload,str): payload=payload.encode()
                self.send_response(status)
                self.send_header("Content-Type",content_type)
                self.send_header("Content-Length",str(len(payload)))
                self.send_header("Cache-Control","no-store")
                self.send_header("X-Content-Type-Options","nosniff")
                self.send_header("X-Frame-Options","DENY")
                self.send_header("Referrer-Policy","no-referrer")
                self.send_header("Cross-Origin-Resource-Policy","same-origin")
                self.send_header("Content-Security-Policy","default-src 'none'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
                if attachment: self.send_header("Content-Disposition",f'attachment; filename="{attachment}"')
                self.end_headers()
                self.wfile.write(payload)

            def accepted_host(self):
                host=self.headers.get("Host","")
                return host in (f"127.0.0.1:{c.server.server_port}",f"localhost:{c.server.server_port}")

            def same_origin(self):
                origin=self.headers.get("Origin","")
                return not origin or origin in (f"http://127.0.0.1:{c.server.server_port}",f"http://localhost:{c.server.server_port}")

            def authorized(self):
                return secrets.compare_digest(self.headers.get("X-SparkTwin-Token",""),c.token)

            def context(self):
                if not self.accepted_host():
                    self.send(403,{"error":"Invalid Host header"});return False
                if not self.same_origin():
                    self.send(403,{"error":"Cross-origin requests blocked"});return False
                return True

            def require_auth(self):
                if not self.authorized():
                    self.send(401,{"error":"Unauthorized"});return False
                return True

            def read_json(self):
                try:
                    n=int(self.headers.get("Content-Length","-1"))
                    if not 0<=n<=MAX_BODY: raise ValueError("JSON body too large or missing Content-Length")
                    if "application/json" not in self.headers.get("Content-Type",""): raise ValueError("application/json required")
                    result=json.loads(self.rfile.read(n))
                    return result
                except (ValueError,UnicodeError,json.JSONDecodeError) as exc:
                    raise ValueError(f"Malformed JSON: {exc}") from exc

            def do_GET(self):
                if not self.context(): return
                path=urlparse(self.path).path
                if path=="/api/health": return self.send(200,{"name":"SparkTwin","version":__version__,"ready":True})
                if path=="/":
                    html=(WEB/"index.html").read_text(encoding="utf-8").replace("__SPARKTWIN_TOKEN__",c.token)
                    return self.send(200,html,"text/html; charset=utf-8")
                for filename,mimetype in [("/app.js","application/javascript; charset=utf-8"),("/styles.css","text/css; charset=utf-8"),("/mark.svg","image/svg+xml")]:
                    if path==filename:
                        data=(WEB/filename.lstrip("/")).read_bytes()
                        return self.send(200,data,mimetype)
                if path.startswith("/api/"):
                    if not self.require_auth(): return
                    try:
                        if path=="/api/bootstrap":
                            return self.send(200,{"version":__version__,"default":DEFAULT,"profiles":PROFILES,
                                                  "scenarios":c.store.list_scenarios(),"benchmarks":c.store.list_benchmarks()})
                        if path=="/api/scenarios": return self.send(200,c.store.list_scenarios())
                        if path=="/api/benchmarks": return self.send(200,c.store.list_benchmarks())
                        if path=="/api/ssh/aliases": return self.send(200,{"hosts":aliases()})
                        if path=="/api/export":
                            return self.send(200,c.store.export(),attachment="sparktwin-backup.json")
                    except Exception:
                        return self.send(500,{"error":"Local storage request failed"})
                    return self.send(404,{"error":"Unknown API route"})
                self.send(404,{"error":"Not found"})

            def do_POST(self):
                if not self.context() or not self.require_auth(): return
                path=urlparse(self.path).path
                try:
                    data=self.read_json()
                    if path=="/api/assess":
                        report=assess(data)
                        report["variants"]=recommend_variant(data)
                        report["calibration"]=calibrate(data,c.store.list_benchmarks())
                        return self.send(200,report)
                    if path=="/api/report":
                        report=assess(data)
                        calibration=calibrate(data,c.store.list_benchmarks())
                        pdf=report_pdf(report,calibration)
                        return self.send(200,pdf,"application/pdf",attachment="sparktwin-assessment.pdf")
                    if path=="/api/scenarios":
                        if not isinstance(data,dict): raise ValueError("Scenario must be an object")
                        ident=c.store.save_scenario(data.get("scenario",data),data.get("id"))
                        return self.send(201,{"id":ident})
                    if path=="/api/benchmarks/import":
                        count=c.store.insert_benchmarks(data)
                        return self.send(201,{"imported":count})
                    if path=="/api/ssh/inspect":
                        if not isinstance(data,dict): raise ValueError("JSON object expected")
                        return self.send(200,inspect(data.get("host","")))
                    if path=="/api/restore":
                        if not isinstance(data,dict) or data.get("format")!="sparktwin-backup-v1":
                            raise ValueError("Unsupported backup format")
                        ss=data.get("scenarios",[]);bs=data.get("benchmarks",[])
                        if not isinstance(ss,list) or not isinstance(bs,list) or len(ss)>500 or len(bs)>500:
                            raise ValueError("Invalid backup size")
                        # Pre-validate everything to reject invalid backups without partial changes.
                        from .model import normalize
                        from .calibration import validate_record
                        safe_ss=[normalize(x) for x in ss]
                        safe_bs=[validate_record(x) for x in bs]
                        for s in safe_ss: c.store.save_scenario(s)
                        if safe_bs: c.store.insert_benchmarks(safe_bs)
                        return self.send(201,{"scenarios":len(safe_ss),"benchmarks":len(safe_bs)})
                except (InvalidScenario,ValueError,KeyError,TypeError) as e:
                    return self.send(400,{"error":str(e)[:400]})
                except RuntimeError as e:
                    return self.send(422,{"error":str(e)[:450]})
                except Exception:
                    return self.send(500,{"error":"Operation failed; see local application logs"})
                self.send(404,{"error":"Unknown API route"})

            def do_DELETE(self):
                if not self.context() or not self.require_auth(): return
                path=urlparse(self.path).path
                if path.startswith("/api/scenarios/"):
                    return self.send(200,{"deleted":c.store.remove_scenario(path.rsplit('/',1)[-1])})
                if path.startswith("/api/benchmarks/"):
                    return self.send(200,{"deleted":c.store.remove_benchmark(path.rsplit('/',1)[-1])})
                return self.send(404,{"error":"Unknown API route"})

        self.server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
        self.server.daemon_threads=True
        self.url=f"http://127.0.0.1:{self.server.server_port}"
        return self

    def serve(self):
        if not self.server: self.start()
        try: self.server.serve_forever(poll_interval=.1)
        finally: self.close()

    def close(self):
        if self.server:
            self.server.server_close()
            self.server=None
        self.store.close()


def main():
    parser=argparse.ArgumentParser(description="SparkTwin local inference planning workbench")
    parser.add_argument("--port",type=int,default=0,help="Local port (default: random)")
    parser.add_argument("--no-browser",action="store_true")
    args=parser.parse_args()
    app=Controller().start(port=args.port)
    print(f"SparkTwin v{__version__} is running at {app.url} (localhost only)",flush=True)
    if not args.no_browser: webbrowser.open(app.url)
    try: app.serve()
    except KeyboardInterrupt: print("\nSparkTwin stopped.")


if __name__=="__main__": main()
