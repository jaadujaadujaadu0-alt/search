admins = {8011957004}
groups = set()
terms = set()

def add_admin(chat_id):
    admins.add(chat_id)

def remove_admin(chat_id):
    admins.discard(chat_id)

def add_group(chat_id):
    groups.add(chat_id)

def remove_group(chat_id):
    groups.discard(chat_id)

def add_term(term):
    terms.add(term)

def remove_term(term):
    terms.discard(term)
