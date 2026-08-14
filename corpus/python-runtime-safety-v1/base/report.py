import subprocess


def render_report(user_name: str, rows: list[str]) -> list[str]:
    subprocess.run(["report", "--user", user_name], check=True)
    return rows
