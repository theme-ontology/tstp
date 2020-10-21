def remove_word_wrap_column_width_newlines(text):
    """
    Remove single newline characters (i.e. '\n') from string, but leave double newlines (i.e. '\n\n').
    Args:
        text: string
    Returns: string
    """
    text_blocks = text.rstrip().split("\n\n")
    newline_free_text_blocks = []

    for text_block in text_blocks:
        newline_free_text_blocks.append(text_block.replace("\n", " "))

    return "\n\n".join(newline_free_text_blocks)
