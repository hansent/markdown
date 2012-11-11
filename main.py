import glob
import os.path
import tempfile
import subprocess
import jinja2


_tmpl_src = open('templates/_default_.html').read()
_default_template = jinja2.Template(_tmpl_src)


def markdown(text):
    f_in = tempfile.TemporaryFile()
    f_out = tempfile.TemporaryFile()

    rb = subprocess.Popen(['ruby', 'markdown.rb'],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )
    html, err_out =  rb.communicate(text)
    if rb.returncode:
        raise Exception(err_out)
    return html


def render_file(fname, outfile):
    name = os.path.basename(fname[:-3])
    source = open(fname, 'r').read()
    content = markdown(source)

    template = _default_template
    try:
        tmpl_file = "templates/{0}.html".format(name)
        template_source = open(tmpl_file, 'r').read()
        template = Template(template_source)
    except:
        pass
    output = template.render(content=content, name=name)
    open(outfile, 'w').write(output)





for f in glob.glob('content/*.md'):
    target = f.replace("content", "public").replace(".md", ".html")
    render_file(f, target)


