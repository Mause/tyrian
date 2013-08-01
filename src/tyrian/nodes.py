

class Node(object):
    """
    Base object for Node's
    """
    # parent = None

    def disolve(self):
        pass


class ParseTree(object):
    """
    Is the overruling object returned from the parser
    """
    def __init__(self, expressions):
        # lisp is ultimately expression based
        for expr in expressions:
            assert type(expr) == ListNode, expr
        self.expressions = expressions

    def __repr__(self):
        return '<ParseTree len(expressions)=={}>'.format(len(self.expressions))

    def pprint(self, node):
        return '\n'.join(self._pprint(self))

    def _pprint(self, node, indent=0):
        cur_lines = []
        cur_lines.append('{}{}'.format('\t' * indent, node))

        if type(node) == ListNode:
            for sub_node in node.elements:
                cur_lines += self.pprint(sub_node, indent + 1)
                cur_lines.append('<ListNode END>{}'.format('\t' * indent))

        return cur_lines


class ListNode(Node):
    """
    Represents a ()
    """
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return '<ListNode len(elements)=={}>'.format(len(self.elements))

    def disolve(self):
        print('disolving')
        new_elements = []
        for element in self.elements:
            result = element.disolve()
            if result is None:
                new_elements.append(element)
            else:
                new_elements.append(result)

        self.elements = new_elements


class IDNode(Node):
    "Represents an ID"
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<IDNode id="{}">'.format(self.id)


class NumberNode(Node):
    "Represents a number"
    def __init__(self, number):
        self.number = int(number)

    def __repr__(self):
        return '<NumberNode number="{}">'.format(self.number)


class StringNode(Node):
    "Represents a string, per se"
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return '<StringNode string="{}">'.format(self.string)
