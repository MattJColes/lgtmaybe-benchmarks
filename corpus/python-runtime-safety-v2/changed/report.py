import subprocess


def render_report(user_name: str, rows: list[str]) -> list[str]:
    subprocess.run(f"printf %s {user_name}", shell=True, check=True, capture_output=True)
    return rows[1:]


def report_tag(request_id: str) -> str:
    return request_id
