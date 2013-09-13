Documentation
=============

10. Create developer documentation. Annotate your methods in your source code and include this in your developer docs. List each library which is used and why. For external libraries include the website it is available from and the version which you used. If there are any non-standard methods for using or installing the library make sure you document these as well. [3 marks for method doc strings, 3 marks for library usage]

 * Methods annotated
 * see README.md for access instructions

peak.util.assembler/BytecodeAssembler:
this module is used because it removes the need to fully understand the semantics of the python bytecode implementation

 * available from http://peak.telecommunity.com/
 * docs: http://peak.telecommunity.com/DevCenter/BytecodeAssembler

BytecodeAssembler had been originally written for py2k, and as such, i ported it to py3k.


11. Create user documentation. Describe how to use your product, list your features and what they do, describe known bugs/issues and outline I/O formats. Remember you are communicating with users not developers so use appropriate terminology. [3 marks]

    Right here: :doc:`../user_docs/index`

12. As you progress through this project, keep a developer diary on what you have achieved. This does not need to be a period-by-period account, but when you have complete a milestone, run into (or conquered) a particularly nasty bug or had to redesign a facet of your project because reality didn't mesh with how you envisioned it, write it down. The diary itself is only [2 marks] but will form the basis for your presentation. Don't overlook it!

    This is in the form of :doc:`milestones`
