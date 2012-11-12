import sys
import os.path
import tempfile
import subprocess
import glob
import jinja2
import watchdog.observers
import watchdog.events
import socket
import SocketServer
import SimpleHTTPServer


class SiteBuilder(watchdog.events.FileSystemEventHandler):
    def __init__(self, **kwargs):
        super(SiteBuilder, self).__init__()
        self.content_path = kwargs.get('content_path', 'content')
        self.output_path = kwargs.get('output_path', 'public')
        self.template_path = kwargs.get('template_path', 'templates')
        self.default_template = kwargs.get('default_template', '_default.html')
        self.template_cache = {}

    def get_template(self, template):
        if not template in self.template_cache:
            tmpl_file = os.path.join(self.template_path, template)
            tmpl_src =  open(tmpl_file).read()
            self.template_cache[template] = jinja2.Template(tmpl_src)
        return self.template_cache[template]

    def markdown(self, text):
        f_in = tempfile.TemporaryFile()
        f_out = tempfile.TemporaryFile()

        flog_path = os.path.dirname(__file__)
        rscript = os.path.join(flog_path, 'markdown.rb')
        rb = subprocess.Popen(['ruby', rscript],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        html, err_out =  rb.communicate(text)
        if rb.returncode:
            raise Exception(err_out)
        return html

    def render_file(self, fname, outfile):
        source = open(fname, 'r').read()
        name = os.path.basename(fname).replace('.md', '')
        content = self.markdown(source)
        try:
            self.get_template("{0}.html".format(name))
            template_source = open(tmpl_file, 'r').read()
            template = Template(template_source)
        except:
            template = self.get_template(self.default_template)
        output = template.render(content=content, name=name)
        open(outfile, 'w').write(output)

    def build(self):
        md_files = os.path.join(self.content_path, "*.md")
        for f in glob.glob(md_files):
            fout = os.path.basename(f).replace('.md', '.html')
            fout = os.path.join(self.output_path, fout)
            self.render_file(f, fout)

    def keep_rebuilding(self):
        self.build()
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self, self.content_path, recursive=True)
        self.observer.start()

    def stop_rebuilding(self):
        self.observer.stop()
        self.observer.join()

    def on_any_event(self, event):
        # if its created we also get a modified event
        # anyways, and we dont want to build twice!
        if event.event_type != 'created':
            self.build()

    def start_http_server(self, host="0.0.0.0", port=8000):
        handler_cls = SiteRequestHandler
        handler_cls.root = self.output_path
        self.httpd = SiteTCPServer((host,port), SiteRequestHandler)
        self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.httpd.serve_forever()

    def stop_http_server(self):
        self.httpd.shutdown()
        self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_dev_server(self, host="0.0.0.0", port=8000):
        try:
            self.keep_rebuilding()
            self.start_http_server(host, port)
        except KeyboardInterrupt:
            self.stop_rebuilding()
            self.stop_http_server()
        finally:
            print "shuting dow..."


class SiteRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    root = "public"
    def translate_path(self, path):
        path = self.root + path
        return os.path.abspath(path)


class SiteTCPServer(SocketServer.TCPServer):
    allow_reuse_address = True


