input_file = "config.toml"
output_file = "config.toml"

with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

# Split into blocks
blocks = []
current = []

for line in text.splitlines():
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

        # Handle multiline strings
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

        # New config entry
        if "=" in line:
            if current_group:
                groups.append(current_group)
            current_group = [line]
        else:
            current_group.append(line)

    if current_group:
        groups.append(current_group)

    # Sort by first line of each group
    groups.sort(key=lambda g: g[0].lower())

    result = [header]

    for g in groups:
        result.extend(g)

    return result

# Sort blocks A-Z
blocks.sort(key=lambda b: b[0].strip("[]").lower())

# Sort internals
blocks = [sort_block(b) for b in blocks]

# Rebuild
# Rebuild with ONLY one empty line between blocks
final_text = "\n\n".join(
    "\n".join(line.rstrip() for line in b).strip()
    for b in blocks
).strip() + "\n"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"Sorted file written to: {output_file}")