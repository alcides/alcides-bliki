from django import template
import re
import pygments
import pygments.lexers as lexers
import pygments.formatters as formatters

register = template.Library()

regex = re.compile(r'<code>(.*?)</code>', re.DOTALL)

@register.filter(name='pygmentize')
def pygmentize(value):
    try:
        last_end = 0
        to_return = ''
        found = 0
        for match_obj in regex.finditer(value):
            code_string = match_obj.group(1)
            try:
                lexer = lexers.guess_lexer(code_string)
            except ValueError:
                lexer = lexers.PythonLexer()
            pygmented_string = pygments.highlight(code_string, lexer, formatters.HtmlFormatter())
            to_return = to_return + value[last_end:match_obj.start(1)] + pygmented_string
            last_end = match_obj.end(1)
            found = found + 1
        to_return = to_return + value[last_end:]
        to_return += u"<style>%s</style>" % formatters.HtmlFormatter().get_style_defs('.highlight')
        return to_return
    except:
        return value