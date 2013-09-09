System Development
==================

4. List and describe the minimum features which will need to be implemented for your project to be considered 'successful'. [3 marks]

 * Lex, parse, and compile a simple program successfully
 * Have comprehensive documentation
 * Have a simple program run with correct behaviour in the Python VM
 * Have basic syntax error detection and notification - full syntax checking does not seem to be possible with a recursive decent parser
 * have a niceish command line interface


5. How will you evaluate performance of your product? Describe three (3) non-trivial (i.e. not 'program doesn't crash') key performance indicators. [6 marks]

 * Does not use excessive amounts of memory
 * Runs a simple program within a decent timeframe
 * compile a program within a decent timeframe


6. Create a set of Data Flow Diagrams for your project (at least the Context Diagram and Level 0 DFD - Level 1 if required). [10 marks]

    This is in the form of :doc:`charts`

7. Using your list of features from Part 4, estimate the time it will take to reach them. Create a Gantt or PERT chart for your timeline. Make sure you keep an eye on this, as it will be a significant part of your final presentation. [3 marks]

    <expand>

8. Describe at least two areas which could be used to extend your project in future revisions and provide some discussion on what would be required to pursue them. [4 marks]

 * Try and have the output be compatible between py3k revisions
 * Optimization of the compiled output (this and the one above may be mutually exclusive)
 * have it be a full lisp machine, with support for lisp macros (the horror!)

9. Develop and test your project. You must include:

Pseudocode and a flow chart for one small module of code (must include loops and conditional branching [if statement]) [4 marks]

See the System Development flow chart on the :doc:`charts` page

And Pseudocode;

.. code-block:: none

    rules <- rules.replace('\n', ' ')
    rules <- rules.split(';')
    rules <- remove excess whitespace
    rules <- remove empty rules

    while rules do
        rule <- pop from rules

        if rule starts with % then
            handle_setting
        else if rule starts with // then
            continue
        else then
            key, *value <- rule split by ::=

            key <- key uppercased and stripped of spaces

            value <- value joined with ::=

            value <- value cleaned

            loaded_grammars[key] <- value
        end
    end

Test data for the grammar_parser is available in the tyrian/Grammar folder,
test data for the project in general is available in the examples folder.
Trace table was deemed to expensive to complete within time remaining, for not
enough marks.
Source code should be included.
