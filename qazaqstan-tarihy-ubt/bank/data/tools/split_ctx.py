import re
def split_context(stem):
    """Ұзын мәнмәтінді «мәтін» + «сұрақ» деп екіге бөледі."""
    s = stem.strip()
    # сұрақ әдетте соңғы сөйлем және ':' белгісімен бітеді
    if s.endswith(':'):
        parts = re.split(r'(?<=[.!?»])\s+', s)
        if len(parts) > 1:
            return ' '.join(parts[:-1]).strip(), parts[-1].strip()
    m = list(re.finditer(r'(?<=[.!?»])\s+', s))
    if m:
        i = m[-1].end()
        return s[:i].strip(), s[i:].strip()
    return s, ''
