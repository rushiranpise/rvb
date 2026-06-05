import argparse

def main():
    parser = argparse.ArgumentParser(description="Sort TOML blocks and keys.")
    parser.add_argument("--ignore-first", type=int, default=0,
                        help="Ignore first N lines (keep them untouched, no sorting)")
    parser.add_argument("--input", default="config.toml", help="Input file")
    parser.add_argument("--output", default="config.toml", help="Output file")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    ignore_first = args.ignore_first

    # Read lines preserving newline characters
    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Split into untouched header and the rest to process
    if ignore_first >= len(all_lines):
        # Nothing to process – just copy the file
        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(all_lines)
        print(f"Copied untouched (all lines ignored) to: {output_file}")
        return

    header_lines = all_lines[:ignore_first]          # exact original lines
    rest_lines = all_lines[ignore_first:]            # lines to be sorted

    # Rebuild the rest part into a single string (our processing expects a string)
    rest_text = "".join(rest_lines)

    # --- existing processing logic (works on rest_text) ---
    # Split into blocks
    blocks = []
    current = []

    for line in rest_text.splitlines():
        if line.startswith('['):
            if current:
                blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)

    # Sort contents inside each block
    def sort_block(block):
        header = block[0]
        content = block[1:]

        groups = []
        current_group = []
        multiline = False

        for line in content:
            stripped = line.strip()

            if '"""' in stripped:
                current_group.append(line)
                if stripped.count('"""') == 1:
                    multiline = not multiline
                if not multiline:
                    groups.append(current_group)
                    current_group = []
                continue

            if multiline:
                current_group.append(line)
                continue

            if "=" in line:
                if current_group:
                    groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)

        if current_group:
            groups.append(current_group)

        groups.sort(key=lambda g: g[0].lower())

        result = [header]
        for g in groups:
            result.extend(g)
        return result

    # Sort blocks A-Z
    blocks.sort(key=lambda b: b[0].strip("[]").lower())
    # Sort internals
    blocks = [sort_block(b) for b in blocks]

    # Rebuild processed part with exactly one empty line between blocks
    processed_text = "\n\n".join(
        "\n".join(line.rstrip() for line in b).strip()
        for b in blocks
    ).strip()
    if processed_text:
        processed_text += "\n"   # trailing newline for consistency

    # --- Combine untouched header and processed part ---
    # Header lines already contain their original newlines.
    # We write them as they are, then the processed text.
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(header_lines)      # untouched lines
        f.write(processed_text)         # sorted rest

    print(f"Ignored first {ignore_first} line(s). Sorted the rest.")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    main()
