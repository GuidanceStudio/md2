"""M92: install.sh syncs the user templates after binary reinstall.

Without this, edits to `md2/templates/default/style.css` are deployed
to the binary but the user's `~/.md2/templates/default/style.css` keeps
the old version (md2 reads from the user dir at render time).
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "install.sh"


def test_install_sh_copies_templates_to_user_dir():
    """install.sh contains a step that copies the bundled templates to
    `~/.md2/templates/` after the binary install."""
    text = INSTALL_SH.read_text(encoding="utf-8")
    # Look for a copy command targeting the user template directory
    has_sync = (
        ".md2/templates" in text
        and ("cp -r" in text or "cp -a" in text or "rsync" in text)
    )
    assert has_sync, (
        "install.sh should sync md2/templates/* to ~/.md2/templates/ after "
        "reinstalling the binary, otherwise CSS edits don't reach rendering"
    )


def test_install_sh_sync_runs_after_uv_install():
    """The sync command appears AFTER the `uv tool install` line, so it
    runs only when the binary install succeeded."""
    text = INSTALL_SH.read_text(encoding="utf-8")
    uv_idx = text.find("uv tool install")
    sync_idx = text.find(".md2/templates")
    assert uv_idx != -1, "expected uv tool install command"
    assert sync_idx != -1, "expected user template sync"
    assert sync_idx > uv_idx, (
        "template sync should run after uv install, not before"
    )
