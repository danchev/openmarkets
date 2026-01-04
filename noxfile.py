#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["nox"]
# ///
import nox

python_versions = ["3.12", "3.13", "3.14"]


@nox.session(venv_backend="uv", python=python_versions)
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.run_install(
        "uv",
        "sync",
        "--group=test",
        "--upgrade",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", "-n", "auto", *session.posargs)


if __name__ == "__main__":
    nox.main()
