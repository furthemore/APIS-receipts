import textwrap


class ReceiptFormatter(object):
    def __init__(self, width=48):
        self.width = 48
        self.margin = 2

    def format_line_item(self, left, right):
        if len(left) + len(right) + self.margin > self.width:
            # Truncate left text to fit:
            left_max_len = self.width - len(right) - self.margin
            left = left[:left_max_len]

        space_len = self.width - len(left) - len(right) - self.margin
        return f"{left}{' '*space_len}  {right}"

    def center_text(self, text):
        space_left = int((self.width - len(text)) / 2)
        return f"{' '*space_left}{text}"

    def right_text(self, text):
        return self.format_line_item("", text)

    def wrap(self, text):
        return textwrap.fill(text, width=self.width)

    def wrap_center(self, text):
        lines = textwrap.wrap(textwrap.dedent(text), width=self.width)
        centered_lines = [self.center_text(line) for line in lines]
        return "\n".join(centered_lines)

    def hr(self, width=None, character="—", center=True):
        if width is None:
            width = self.width
        if center:
            return self.center_text(character * width)
        return character * width


if __name__ == "__main__":
    sample_paragraph = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
    builder = ReceiptFormatter()

    print()
    print(builder.center_text("FurTheMore 2020"))
    print()

    line_items = [
        ["Regular Badge", "$490.00"],
        ["Con Book", "$0.00"],
        ["Tee-shirt (Medium)", "$25.00"],
        ["Discount", "-$15.99"],
    ]

    for line in line_items:
        print(builder.format_line_item(line[0], line[1]))

    print()

    print(builder.format_line_item("Donation to FurTheMore 2020", "$10.00"))
    print(builder.format_line_item("Donation to ALS Society", "$10.00"))

    print()

    print(builder.right_text("Total Due:   $580.01"))
    print()
    print(builder.hr())
    print()

    print(builder.format_line_item("VISA CREDIT **** 4425", "$580.01"))
    print("Ref: U4REQT | AID: A0000000031010")
    print("Auth: 025993")
    print("Completed: 2020-02-25T07:26:36.951Z")
    print()

    print(builder.hr())
    print()

    print(builder.wrap_center(sample_paragraph))
