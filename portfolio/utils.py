import ipaddress


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    candidates = forwarded_for.split(',') if forwarded_for else []
    candidates.append(request.META.get('REMOTE_ADDR', ''))

    for candidate in candidates:
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except ValueError:
            continue
    return None
