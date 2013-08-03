import warnings

from .utils import reduce


class ParseTree(object):
    """
    Is the overruling object returned from the parser
    """
    def __init__(self, expressions):
        # lisp is ultimately expression based
        self.expressions = expressions

    def __repr__(self):
        return '<ParseTree len(expressions)=={}>'.format(len(self.expressions))

    def pprint(self):
        return '\n'.join(self._pprint(self.expressions))

    def _pprint(self, node, indent=0):
        cur_lines = []
        cur_lines.append('{}{}'.format('\t' * indent, node))

        if type(node) in [ListNode, ContainerNode, list]:
            if issubclass(type(node), Node):
                for sub_node in node.content:
                    cur_lines += self._pprint(sub_node, indent + 1)
            else:
                for sub_node in node:
                    cur_lines += self._pprint(sub_node, indent + 1)
            name = node.__qualname__ if hasattr(node, '__qualname__') else node
            cur_lines.append('{}</{}>'.format(
                '\t' * indent,
                name))

        return cur_lines


class Node(object):
    """
    Base object for Node's
    """
    def disolve(self):
        pass


class ListNode(Node):
    """
    Represents a () in LISP
    """
    def __init__(self, content, strip=True):
        if strip:
            content = content[1:-1]
        self.content = reduce(content)

    def __repr__(self):
        return '<{} len(content)=={}>'.format(
            self.__qualname__,
            len(self.content))

    def disolve(self):
        print('disolving')
        new_content = []
        for element in self.content:
            result = element.disolve()
            if result is None:
                new_content.append(element)
            else:
                new_content.append(result)

        self.content = new_content


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

# and we define the mappings

grammar_mapping = {
    "list": ListNode,
    "string": StringNode,
    "id": IDNode
}
