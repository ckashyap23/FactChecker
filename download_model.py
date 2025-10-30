import os
import sys
import argparse
from pathlib import Path

try:
    from huggingface_hub import snapshot_download, login
except ImportError as e:
    print("huggingface_hub is required. Install with: pip install --upgrade huggingface_hub")
    raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a model repository from Hugging Face Hub to a local directory."
    )
    parser.add_argument(
        "--repo-id",
        default="mistralai/Mistral-7B-Instruct-v0.3",
        help="Hugging Face repository id (e.g., org/name).",
    )
    parser.add_argument(
        "--revision",
        default=None,
        help="Optional git revision (branch, tag, or commit SHA).",
    )
    parser.add_argument(
        "--local-dir",
        default=str(Path("models") / "Mistral-7B-Instruct-v0.3"),
        help="Destination directory for the downloaded snapshot.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="Hugging Face access token. Defaults to HF_TOKEN env var if set.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Number of concurrent download workers.",
    )
    parser.add_argument(
        "--no-symlinks",
        action="store_true",
        help="Ignored: snapshot_download no longer uses symlinks when downloading to a local directory.",
    )
    parser.add_argument(
        "--allow-unsafe-symlinks",
        action="store_true",
        help="Ignored: snapshot_download no longer uses symlinks when downloading to a local directory.",
    )
    return parser.parse_args()


def ensure_login(token: str | None) -> None:
    if not token:
        return
    try:
        login(token=token, add_to_git_credential=True)
    except Exception as err:
        print(f"Warning: login failed: {err}")


def main() -> int:
    args = parse_args()

    # Authenticate if token provided
    ensure_login(args.token)

    local_dir = Path(args.local_dir).resolve()
    local_dir.mkdir(parents=True, exist_ok=True)

    if args.no_symlinks or args.allow_unsafe_symlinks:
        print("Note: --no-symlinks/--allow-unsafe-symlinks are ignored; symlinks are not used.")

    print(f"Downloading '{args.repo_id}' to: {local_dir}")

    try:
        snapshot_path = snapshot_download(
            repo_id=args.repo_id,
            revision=args.revision,
            local_dir=str(local_dir),
            max_workers=args.max_workers,
        )
    except Exception as err:
        print("Download failed.")
        print(f"Error: {err}")
        return 1

    print("Download complete.")
    print(f"Files available at: {snapshot_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


