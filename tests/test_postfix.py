from io import StringIO
import re


EQUAL = re.compile(r" *= *")
SPACES = re.compile(r"^\s+")


def postfix_reader(iterator):
    """
    Read postfix config lines, and yield key, value.
    See https://www.oreilly.com/library/view/postfix-the-definitive/0596002122/ch04s02.html
    """
    current = StringIO()
    for line in iterator:
        if line.strip() == "" or line.startswith("#"):
            # empty line or line starting with #
            continue
        if not SPACES.search(line) and current.tell():
            # line doesn't start with space, and current buffer is not empty
            current.seek(0)
            yield tuple(EQUAL.split(current.read(), 1))
            current = StringIO()  # reset the buffer
        current.write(line.lstrip())
    if current.tell():
        current.seek(0)
        yield tuple(EQUAL.split(current.read(), 1))


def test_postfix(host):
    if False:
        proto = dict(
            postfix_reader(
                host.file("/etc/postfix/main.cf.proto").content_string.split("\n")
            )
        )
        print(proto)
    main = host.file("/etc/postfix/main.cf")
    assert main.exists
    for key, value in postfix_reader(main.content_string.split("\n")):
        if value.startswith("hash:"):
            # assert that toto exists with hash:/toto
            path = value.split(":", 1)[1]
            assert host.file(path).exists, "%s doesn't exist" % path
            assert host.file("%s.db" % path).exists, "%s.db doesn't exist" % path
        if value.startswith("regexp:"):
            # assert that toto exists with regexp:/toto
            path = value.split(":", 1)[1]
            assert host.file(path).exists, "%s doesn't exist" % path
