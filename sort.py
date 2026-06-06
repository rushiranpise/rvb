import argparse

def main():
    parser = argparse.ArgumentParser(description="Sort TOML blocks and keys.")
    parser.add_argument("--ignore-first", type=int, default=0,
                        help="Ignore first N lines (keep them untouched, no sorting)")
    parser.add_argument("--input", default="config.toml", help="Input file")
    parser.add_argument("--output", default="config.toml", help="Output file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    ignore = args.ignore_first
    if ignore >= len(all_lines):
        with open(args.output, "w", encoding="utf-8") as f:
            f.writelines(all_lines)
        print(f"Copied untouched (all lines ignored) to: {args.output}")
        return

    header = all_lines[:ignore]
    rest_lines = all_lines[ignore:]

    # Reconstruct the rest as a single string (preserving newlines)
    rest_text = "".join(rest_lines)

    # --- Process the rest: split into blocks, ignoring blank lines ---
    blocks = []
    current_block = []
    in_multiline = False
    multiline_delimiter = None  # not strictly needed, but shows the idea

    for line in rest_text.splitlines():
        # Strip only for detection – we keep original line for output
        stripped = line.strip()

        # Multiline string handling (simplified but robust)
        if '"""' in line:
            # Toggle multiline state if odd number of delimiters
            if line.count('"""') % 2 == 1:
                in_multiline = not in_multiline
            current_block.append(line)
            continue

        if in_multiline:
            current_block.append(line)
            continue

        # Skip completely empty lines (they are not part of any block)
        if stripped == "":
            continue

        # New block starts with a line like [section] or [[section]]
        if line.startswith('[') and line.endswith(']'):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    # --- Sort blocks by section name (case‑insensitive) ---
    blocks.sort(key=lambda b: b[0].strip('[]').lower())

    # --- Sort keys inside each block ---
    def sort_block(block):
        if len(block) <= 1:
            return block
        header = block[0]
        content = block[1:]

        # Group consecutive lines that belong together (e.g., multi‑line values)
        groups = []
        current_group = []
        in_multiline = False

        for line in content:
            stripped = line.strip()
            # Toggle multiline state on odd number of """
            if '"""' in line:
                current_group.append(line)
                if line.count('"""') % 2 == 1:
                    in_multiline = not in_multiline
                if not in_multiline:
                    groups.append(current_group)
                    current_group = []
                continue

            if in_multiline:
                current_group.append(line)
                continue

            if '=' in line:
                if current_group:
                    groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)

        if current_group:
            groups.append(current_group)

        # Sort groups by the first key name (case‑insensitive)
        groups.sort(key=lambda g: g[0].split('=', 1)[0].strip().lower())

        # Rebuild block
        result = [header]
        for g in groups:
            result.extend(g)
        return result

    blocks = [sort_block(b) for b in blocks]

    # --- Rebuild the processed text with consistent spacing ---
    # One blank line between blocks, no blank lines inside blocks
    processed_blocks = []
    for b in blocks:
        # Join block lines with a single newline, strip trailing spaces per line
        block_str = "\n".join(line.rstrip() for line in b)
        processed_blocks.append(block_str)

    processed_text = "\n\n".join(processed_blocks).strip()
    if processed_text:
        processed_text += "\n"   # trailing newline for POSIX compliance

    # --- Write final file ---
    with open(args.output, "w", encoding="utf-8") as f:
        f.writelines(header)      # untouched header lines (original newlines)
        f.write(processed_text)   # sorted rest

    print(f"Ignored first {ignore} line(s). Sorted the rest.")
    print(f"Output written to: {args.output}")

if __name__ == "__main__":
    main()
