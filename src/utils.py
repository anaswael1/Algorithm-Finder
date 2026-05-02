from pygments import lexers
from pygments.lexers import get_lexer_by_name

def apply_syntax_highlighting(textbox, lang_name):
    tk_text = textbox._textbox
    code = textbox.get("1.0", "end-1c")
    
    lexer_map = {
        "python": "python", "c++": "cpp", "cpp": "cpp", 
        "c#": "csharp", "csharp": "csharp", "java": "java"
    }
    
    try:
        from pygments.lexers import get_lexer_by_name
        lexer = get_lexer_by_name(lexer_map.get(lang_name.lower(), "text"))
    except:
        return

    # Enhanced Color Palette
    colors = {
        "Token.Comment.Preproc": "#d19a66",   # Orange/Gold for #include, #define
        "Token.Keyword": "#c678dd",           # Purple
        "Token.Keyword.Type": "#56b6c2",      # Cyan (int, double, char)
        "Token.Name.Function": "#61afef",     # Blue
        "Token.Name.Class": "#e5c07b",        # Yellow
        "Token.String": "#98c379",            # Green
        "Token.Comment": "#5c6370",           # Dark Grey for actual comments
        "Token.Operator": "#56b6c2",          # Cyan
        "Token.Number": "#d19a66",            # Orange
    }

    for token_name, color in colors.items():
        tk_text.tag_configure(token_name, foreground=color)

    for tag in tk_text.tag_names():
        tk_text.tag_remove(tag, "1.0", "end")

    for index, token, value in lexer.get_tokens_unprocessed(code):
        token_str = str(token)
        
        # KEY FIX: Sort keys by length descending to match 
        # 'Token.Comment.Preproc' before 'Token.Comment'
        matched_tag = None
        for tag_key in sorted(colors.keys(), key=len, reverse=True):
            if token_str.startswith(tag_key):
                matched_tag = tag_key
                break
        
        if matched_tag:
            start = f"1.0 + {index} chars"
            end = f"1.0 + {index + len(value)} chars"
            tk_text.tag_add(matched_tag, start, end)