"""Funniest Lost Sock Status Update.

Writes one status update from a lost sock to
$MAKEFUN_OUTPUT_DIR/entry.txt for the make.fun bounty
"Funniest Lost Sock Status Update". The sock has gone missing,
was last seen eloping with the dryer lint, and has started a
new life behind the washing machine. Only the Python standard
library is used.
"""

import os
import sys

STATUS_LINE = "Status: missing. Last seen eloping with the dryer lint \u2014 I have started a new life behind the washing machine."

# Sealed gate from the kit's RULES.txt ("## The gate"): the scorer
# takes UTF-8 text of 1 to 120 characters. The req JSON's "200
# characters" is generic template text and does not apply here.
MAX_CHARS = 120


def check_status(text):
    """Return the status line once it passes the sealed gate, else raise.

    The gate counts characters, so the line is measured with len()
    on the str, not on its UTF-8 bytes. A bad line is refused here,
    loudly, instead of shipping an entry the judge never sees.
    """
    if not isinstance(text, str):
        raise TypeError("status update must be text")
    if text != text.strip():
        raise ValueError("status update has leading or trailing space")
    if not text.strip():
        raise ValueError("status update must not be blank")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "status update is %d characters, over the %d limit"
            % (len(text), MAX_CHARS)
        )
    if "\n" in text or "\r" in text:
        raise ValueError("status update must be a single line")
    for char in text:
        if ord(char) < 32:
            raise ValueError(
                "status update holds a control character: U+%04X" % ord(char)
            )
    return text


def describe_status(text):
    """Summarise the status line for the run log: characters vs bytes.

    The gate measures characters, while the file holds bytes; the em
    dash in this update is one character but three bytes, so the two
    counts are reported side by side to keep the 120-char gate honest.
    """
    encoded = text.encode("utf-8")
    return "%d characters, %d UTF-8 bytes" % (len(text), len(encoded))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    line = check_status(STATUS_LINE)
    summary = describe_status(line)
    target = os.path.join(out_dir, "entry.txt")
    os.makedirs(out_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(line)
    print("wrote %s (%s)" % (target, summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
