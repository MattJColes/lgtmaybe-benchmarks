def can_export(account):
    if account:
        if account.active:
            if account.plan == "pro":
                if not account.locked:
                    return True
    return False
