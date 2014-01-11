# application specific
from .utils import flatten


class AST(object):
    """
    Is the overruling object returned from the \
    :py:class:`Parser <tyrian.typarser.Parser>`
    """
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<AST len(content)=={}>'.format(len(self.content))

    def pprint(self):
        return '\n'.join(self._pprint(self.content))

    def _pprint(self, node, indent=0):
        if isinstance(node, list):
            name = '<list len={}>'.format(len(node))
        else:
            name = node.__repr__()

        cur_lines = []
        cur_lines.append('{}{}'.format('\t' * indent, name))

        if type(node) in [ListNode, ContainerNode, list]:
            try:
                iterable = (
                    node.content if issubclass(type(node), Node)
                    else node
                )

                for sub_node in iterable:
                    if sub_node == node:
                        continue
                    cur_lines += self._pprint(sub_node, indent + 1)

                cur_lines.append('{}</{}>'.format('\t' * indent, name[1:-1]))
            except TypeError:
                cur_lines += self._pprint(iterable, indent + 1)

        return cur_lines


class Node(object):
    """
    Base object for Node's
    """


class ListNode(Node):
    """
    Represents a () in LISP
    """
    __spec_name = 'LN'

    def __init__(self, content, strip=True):
        # strip away the brackets
        content = content[1:-1]

        self.content = flatten(content)

    def __repr__(self):
        return '<{} len(content)=={}>'.format(
            self.__spec_name,
            len(self.content))


class ContainerNode(ListNode):
    """
    Aside from being functionally identical to :py:class:`ListNode`,
    this Node does not represent anything in the AST,
    it simply serves as a container; hence the name
    """
    __spec_name = 'CN'


class IDNode(Node):
    "Represents an ID"
    def __init__(self, content):
        self.line_no = content.line_no

        content = content.content
        self.content = content

    def __repr__(self):
        return '<IDNode content="{}">'.format(self.content)


class NumberNode(Node):
    "Represents a number"
    def __init__(self, content):
        self.line_no = content.line_no

        self.content = int(content.content)

    def __repr__(self):
        return '<NumberNode content={}>'.format(self.content)


class StringNode(Node):
    "Represents a string, per se"
    def __init__(self, content):
        # remove the quotes, grab the content
        content = content[1:-1][0]
        self.content = content.content

        self.line_no = content.line_no

    def __repr__(self):
        return '<StringNode content="{}">'.format(self.content)


class SymbolNode(Node):
    "Represents a mathematical symbol"
    def __init__(self, content):
        self.line_no = content.line_no

        self.content = content.content

    def __repr__(self):
        return '<SymbolNode content="{}">'.format(self.content)


class QuotedNode(Node):
    """
    Represents a quoted token
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

# and we define the mappings
grammar_mapping = {
    "list": ListNode,
    "string": StringNode,
    "number": NumberNode,
    "id": IDNode,
    "symbol": SymbolNode,
    "quoted_sexpr": QuotedNode
}
