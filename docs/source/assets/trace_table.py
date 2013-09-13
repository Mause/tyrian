loaded_grammars = {}
handle_setting = lambda: None
clean = lambda x: x.strip()
rules = '''\
word ::= words words words;
words ::= "blah" "blah" "blah";
'''
# code that we are tracing follows


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
