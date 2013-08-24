# import unittest.mock
from functools import wraps
import sphinx.ext.graphviz


def mend_render_dot(func):
    func.__mended__ = True

    @wraps(func)
    def wrapper(code, *args, **kwargs):
        code = code.encode('utf-8')
        return func(code, *args, **kwargs)


def mend():
    from unittest.mock import patch
    render_dot = mend_render_dot(sphinx.ext.graphviz.render_dot)
    patch('sphinx.ext.graphviz.render_dot', render_dot)



# def render_dot(self, code, options, format, prefix='graphviz'):
#     """Render graphviz code into a PNG or PDF output file."""
#     hashkey = (
#         code +
#         str(options) +
#         str(self.builder.config.graphviz_dot) +
#         str(self.builder.config.graphviz_dot_args)).encode('utf-8')

#     fname = '%s-%s.%s' % (prefix, sha(hashkey).hexdigest(), format)
#     if hasattr(self.builder, 'imgpath'):
#         # HTML
#         relfn = posixpath.join(self.builder.imgpath, fname)
#         outfn = path.join(self.builder.outdir, '_images', fname)
#     else:
#         # LaTeX
#         relfn = fname
#         outfn = path.join(self.builder.outdir, fname)

#     if path.isfile(outfn):
#         return relfn, outfn

#     if hasattr(self.builder, '_graphviz_warned_dot') or \
#        hasattr(self.builder, '_graphviz_warned_ps2pdf'):
#         return None, None

#     ensuredir(path.dirname(outfn))

#     # graphviz expects UTF-8 by default
#     if isinstance(code, str):
#         code = code.encode('utf-8')

#     dot_args = [self.builder.config.graphviz_dot]
#     dot_args.extend(self.builder.config.graphviz_dot_args)
#     dot_args.extend(options)
#     dot_args.extend(['-T' + format, '-o' + outfn])
#     if format == 'png':
#         dot_args.extend(['-Tcmapx', '-o%s.map' % outfn])
#     try:
#         p = Popen(dot_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
#     except OSError as err:
#         if err.errno != ENOENT:   # No such file or directory
#             raise
#         self.builder.warn('dot command %r cannot be run (needed for graphviz '
#                           'output), check the graphviz_dot setting' %
#                           self.builder.config.graphviz_dot)
#         self.builder._graphviz_warned_dot = True
#         return None, None
#     try:
#         # Graphviz may close standard input when an error occurs,
#         # resulting in a broken pipe on communicate()
#         stdout, stderr = p.communicate(code)
#     except (OSError, IOError) as err:
#         if err.errno not in (EPIPE, EINVAL):
#             raise
#         # in this case, read the standard output and standard error streams
#         # directly, to get the error message(s)
#         stdout, stderr = p.stdout.read(), p.stderr.read()
#         p.wait()
#     if p.returncode != 0:
#         raise GraphvizError('dot exited with error:\n[stderr]\n%s\n'
#                             '[stdout]\n%s' % (stderr, stdout))
#     return relfn, outfn
