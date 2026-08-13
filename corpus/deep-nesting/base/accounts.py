def can_export(account):
    return bool(account and account.active and account.plan == "pro" and not account.locked)
