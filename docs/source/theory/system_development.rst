System Development
==================

4. List and describe the minimum features which will need to be implemented for your project to be considered 'successful'. [3 marks]

 * Lex, parse, and compile a simple program successfully
 * Have comprehensive documentation
 * Have a simple program run with correct behavior in the Python VM
 * Have basic syntax error detection and notification - full syntax checking does not seem to be possible with a recursive decent parser
 * have a nice-ish command line interface


5. How will you evaluate performance of your product? Describe three (3) non-trivial (i.e. not 'program doesn't crash') key performance indicators. [6 marks]

 * Does not use excessive amounts of memory
 * Runs a simple program within a decent time frame
 * compile a program within a decent time frame


6. Create a set of Data Flow Diagrams for your project (at least the Context Diagram and Level 0 DFD - Level 1 if required). [10 marks]

    This is in the form of :doc:`charts`

7. Using your list of features from Part 4, estimate the time it will take to reach them. Create a Gantt or PERT chart for your timeline. Make sure you keep an eye on this, as it will be a significant part of your final presentation. [3 marks]

    See :doc:`assets`

8. Describe at least two areas which could be used to extend your project in future revisions and provide some discussion on what would be required to pursue them. [4 marks]

 * Try and have the output be compatible between py3k revisions
 * Optimization of the compiled output (this and the one above may be mutually exclusive)
 * have it be a full lisp machine, with support for lisp macros (the horror!)

9. Develop and test your project. You must include:



Pseudocode
----------
Pseudocode and a flow chart for one small module of code (must include loops and conditional branching [if statement]) [4 marks]

See the System Development flow chart on the :doc:`charts` page for the flow chart

.. code-block:: pascal

    rules <- in rules replace "\n" with " "
    rules <- rules split by ";"
    rules <- remove excess whitespace from rules
    rules <- remove empty rules

    while rules do
        rule <- pop from rules

        if rule starts with "%" then
            handle_setting
        else if rule starts with "//" then
            continue
        else then
            value <- rule split by "::="
            key <- first from value

            key <- key uppercased and stripped of excess whitespace

            value <- value joined with "::="

            value <- value cleaned

            loaded_grammars[key] <- value
        end if
    end while

Test data
---------
Test data for the grammar_parser is available in the tyrian/Grammar folder,
test data for the project in general is available in the examples folder.

Trace table
-----------

See :doc:`assets` for image

for code

.. code-block:: python

    rules = rules.replace("\n", " ")
    rules = rules.split(";")
    rules = map(str.rstrip, rules)
    rules = list(filter(bool, rules))

    while rules:
        rule = rules.pop(0)

        if rule.startswith("%"):
            handle_setting()
        elif rule.startswith("//"):
            continue
        else:
            value = rule.split("::=")
            key = value.pop(0)

            key = key.upper().strip()

            value = "::=".join(value)

            value = clean(value)

            loaded_grammars[key] = value



Source code
-----------

Source code should be included... somewhere.
