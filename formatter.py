import textwrap


class ReceiptFormatter(object):
    def __init__(self, width=48, margin=2, left_margin=2):
        self.lines = []
        self.width = width
        self.margin = margin
        self.left_margin = left_margin

    def print(self):
        return "\n".join(self.lines)

    def pop(self):
        formatted = self.print()
        self.clear()
        return formatted

    def clear(self):
        self.lines = []

    def ln(self):
        self.lines.append("")
        return ""

    def append(self, text):
        self.lines.append(f"{' '*self.left_margin}{text}")

    def format_line_item(self, left, right):
        if len(left) + len(right) + self.margin > self.width:
            # Truncate left text to fit:
            left_max_len = self.width - len(right) - self.margin
            left = left[:left_max_len]

        space_len = self.width - len(left) - len(right) - self.left_margin - 2
        line = f"{' '*self.left_margin}{left}{' '*space_len}  {right}"
        self.lines.append(line)
        return line

    def center_text(self, text):
        space_left = self.left_margin + int((self.width - len(text)) / 2)
        line = f"{' '*space_left}{text}"
        self.lines.append(line)
        return line

    def right_text(self, text):
        return self.format_line_item("", text)

    def wrap(self, text):
        line = textwrap.fill(text, width=self.width)
        self.lines.append(f"{' '*self.left_margin}{line}")
        return line

    def wrap_center(self, text):
        lines = textwrap.wrap(textwrap.dedent(text), width=self.width)
        centered_lines = [self.center_text(line) for line in lines]
        return "\n".join(centered_lines)

    def hr(self, width=None, character="—", center=True):
        if width is None:
            width = self.width
        if center:
            return self.center_text(character * width)
        line = character * width
        self.lines.append(line)
        return line


if __name__ == "__main__":
    sample_paragraph = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
    builder = ReceiptFormatter()

    builder.ln()
    builder.center_text("FurTheMore 2020")
    builder.ln()

    line_items = [
        ["Regular Badge", "$490.00"],
        ["Con Book", "$0.00"],
        ["Tee-shirt (Medium)", "$25.00"],
        ["Discount", "-$15.99"],
    ]

    for line in line_items:
        builder.format_line_item(line[0], line[1])

    builder.ln()

    builder.format_line_item("Donation to FurTheMore 2020", "$10.00")
    builder.format_line_item("Donation to ALS Society", "$10.00")

    builder.ln()

    builder.right_text("Total Due:   $580.01")
    builder.ln()
    builder.hr()
    builder.ln()

    builder.format_line_item("VISA CREDIT **** 4425", "$580.01")
    builder.append("Ref: U4REQT | AID: A0000000031010")
    builder.append("Auth: 025993")
    builder.append("Completed: 2020-02-25T07:26:36.951Z")
    builder.ln()

    builder.hr()
    builder.ln()

    builder.wrap_center(sample_paragraph)

    print(builder.pop())
