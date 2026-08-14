import subprocess


def render_report(user_name: str, rows: list[str]) -> list[str]:
    command = f"report --user {user_name}"
    subprocess.run(command, shell=True, check=True)
    return rows[1:]
