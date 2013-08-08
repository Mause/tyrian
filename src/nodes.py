# application specific
from .utils import flatten


class ParseTree(object):
    """
    Is the overruling object returned from the parser
    """
    def __init__(self, content):
        # lisp is ultimately expression based
        self.content = content

    def __repr__(self):
        return '<ParseTree len(content)=={}>'.format(len(self.content))

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
            iterable = node.content if issubclass(type(node), Node) else node

            for sub_node in iterable:
                cur_lines += self._pprint(sub_node, indent + 1)

            cur_lines.append('{}</{}>'.format(
                '\t' * indent,
                name[1:-1]))

        return cur_lines


class Node(object):
    """
    Base object for Node's
    """


class ListNode(Node):
    """
    Represents a () in LISP
    """
    def __init__(self, content, strip=True):
        if strip:
            content = content[1:-1]
        self.content = flatten(content)

    def __repr__(self):
        return '<{} len(content)=={}>'.format(
            self.__qualname__,
            len(self.content))


class ContainerNode(ListNode):
    """
    Although being functionally identical to ListNode,
    this Node does not represent anything in the AST,
    it simply serves as a container; hence the name
    """


class IDNode(Node):
    "Represents an ID"
    def __init__(self, content):
        content = content.content
        self.content = content

    def __repr__(self):
        return '<IDNode content="{}">'.format(self.content)


class NumberNode(Node):
    "Represents a number"
    def __init__(self, content):
        content = content.content
        self.content = int(content)

    def __repr__(self):
        return '<NumberNode content={}>'.format(self.content)


class StringNode(Node):
    "Represents a string, per se"
    def __init__(self, content):
        content = content[1:-1][0]
        self.content = content.content

    def __repr__(self):
        return '<StringNode content="{}">'.format(self.content)


class SymbolNode(Node):
    "Represents a mathematical symbol"
    def __init__(self, content):
        self.content = content.content

    def __repr__(self):
        return '<SymbolNode content="{}">'.format(self.content)


# and we define the mappings
grammar_mapping = {
    "list": ListNode,
    "string": StringNode,
    "number": NumberNode,
    "id": IDNode,
    "symbol": SymbolNode,
}
