from sphinx.ext.graphviz import (
    GraphvizError,
    graphviz,
    Graphviz,
    GraphvizSimple,
    mapname_re
)
import posixpath
from os import path
from docutils import nodes
from hashlib import sha1 as sha
from subprocess import Popen, PIPE
from sphinx.util.osutil import ensuredir, ENOENT, EPIPE, EINVAL


def render_dot(self, code, options, format, prefix='graphviz'):
    """Render graphviz code into a PNG or PDF output file."""
    hashkey = code
    hashkey += str(options)
    hashkey += str(self.builder.config.graphviz_dot)
    hashkey += str(self.builder.config.graphviz_dot_args)
    hashkey = hashkey.encode('utf-8')

    fname = '%s-%s.%s' % (prefix, sha(hashkey).hexdigest(), format)
    if hasattr(self.builder, 'imgpath'):
        # HTML
        relfn = posixpath.join(self.builder.imgpath, fname)
        outfn = path.join(self.builder.outdir, '_images', fname)
    else:
        # LaTeX
        relfn = fname
        outfn = path.join(self.builder.outdir, fname)

    if path.isfile(outfn):
        return relfn, outfn

    if hasattr(self.builder, '_graphviz_warned_dot') or \
       hasattr(self.builder, '_graphviz_warned_ps2pdf'):
        return None, None

    ensuredir(path.dirname(outfn))

    # graphviz expects UTF-8 by default
    if isinstance(code, str):
        code = code.encode('utf-8')

    dot_args = [self.builder.config.graphviz_dot]
    dot_args.extend(self.builder.config.graphviz_dot_args)
    dot_args.extend(options)
    dot_args.extend(['-T' + format, '-o' + outfn])
    if format == 'png':
        dot_args.extend(['-Tcmapx', '-o%s.map' % outfn])
    try:
        p = Popen(dot_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('dot command %r cannot be run (needed for graphviz '
                          'output), check the graphviz_dot setting' %
                          self.builder.config.graphviz_dot)
        self.builder._graphviz_warned_dot = True
        return None, None
    try:
        # Graphviz may close standard input when an error occurs,
        # resulting in a broken pipe on communicate()
        stdout, stderr = p.communicate(code)
    except (OSError, IOError) as err:
        if err.errno not in (EPIPE, EINVAL):
            raise
        # in this case, read the standard output and standard error streams
        # directly, to get the error message(s)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        p.wait()
    if p.returncode != 0:
        raise GraphvizError('dot exited with error:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    return relfn, outfn


def render_dot_html(self, node, code, options, prefix='graphviz',
                    imgcls=None, alt=None):
    format = self.builder.config.graphviz_output_format
    try:
        if format not in ('png', 'svg'):
            raise GraphvizError("graphviz_output_format must be one of 'png', "
                                "'svg', but is %r" % format)
        fname, outfn = render_dot(self, code, options, format, prefix)
    except GraphvizError as exc:
        self.builder.warn('dot code %r: ' % code + str(exc))
        raise nodes.SkipNode

    inline = node.get('inline', False)
    if inline:
        wrapper = 'span'
    else:
        wrapper = 'p'

    self.body.append(self.starttag(node, wrapper, CLASS='graphviz'))
    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get('alt', self.encode(code).strip())
        imgcss = imgcls and 'class="%s"' % imgcls or ''
        if format == 'svg':
            svgtag = '<img src="%s" alt="%s" %s/>\n' % (fname, alt, imgcss)
            self.body.append(svgtag)
        else:
            mapfile = open(outfn + '.map', 'rb')
            try:
                imgmap = mapfile.readlines()
            finally:
                mapfile.close()
            if len(imgmap) == 2:
                # nothing in image map (the lines are <map> and </map>)
                self.body.append('<img src="%s" alt="%s" %s/>\n' %
                                 (fname, alt, imgcss))
            else:
                # has a map: get the name of the map and connect the parts
                mapname = mapname_re.match(imgmap[0].decode('utf-8')).group(1)
                self.body.append('<img src="%s" alt="%s" usemap="#%s" %s/>\n' %
                                 (fname, alt, mapname, imgcss))
                self.body.extend([item.decode('utf-8') for item in imgmap])
        if node.get('caption') and not inline:
            self.body.append('</p>\n<p class="caption">')
            self.body.append(self.encode(node['caption']))

    self.body.append('</%s>\n' % wrapper)
    raise nodes.SkipNode


def render_dot_latex(self, node, code, options, prefix='graphviz'):
    try:
        fname, outfn = render_dot(self, code, options, 'pdf', prefix)
    except GraphvizError as exc:
        self.builder.warn('dot code %r: ' % code + str(exc))
        raise nodes.SkipNode

    inline = node.get('inline', False)
    if inline:
        para_separator = ''
    else:
        para_separator = '\n'

    if fname is not None:
        caption = node.get('caption')
        # XXX add ids from previous target node
        if caption and not inline:
            self.body.append('\n\\begin{figure}[h!]')
            self.body.append('\n\\begin{center}')
            self.body.append('\n\\caption{%s}' % self.encode(caption))
            self.body.append('\n\\includegraphics{%s}' % fname)
            self.body.append('\n\\end{center}')
            self.body.append('\n\\end{figure}\n')
        else:
            self.body.append('%s\\includegraphics{%s}%s' %
                             (para_separator, fname, para_separator))
    raise nodes.SkipNode


def latex_visit_graphviz(self, node):
    render_dot_latex(self, node, node['code'], node['options'])


def html_visit_graphviz(self, node):
    render_dot_html(self, node, node['code'], node['options'])


def setup(app):
    app.add_node(graphviz,
                 html=(html_visit_graphviz, None),
                 latex=(latex_visit_graphviz, None))
    app.add_directive('graphviz', Graphviz)
    app.add_directive('graph', GraphvizSimple)
    app.add_directive('digraph', GraphvizSimple)
    app.add_config_value('graphviz_dot', 'dot', 'html')
    app.add_config_value('graphviz_dot_args', [], 'html')
    app.add_config_value('graphviz_output_format', 'png', 'html')
