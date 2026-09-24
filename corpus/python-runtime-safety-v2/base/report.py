import subprocess


def render_report(user_name: str, rows: list[str]) -> list[str]:
    subprocess.run(["printf", "%s", user_name], check=True, capture_output=True)
    return rows


def report_tag(request_id: str) -> str:
    return "request:" + request_id
