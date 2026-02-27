""" Main entry point for PBS Job Monitor & Notifier.

This script wraps the qsub command and starts a background monitor
for the submitted job.
"""

import subprocess
import sys
import argparse
from config_loader import ConfigurationLoader
from monitor import main as monitor_main


def parse_job_id(qsub_output: str) -> str:
    """Parse the Job ID from qsub command output.

    Args:
        qsub_output: The stdout output from the qsub command.

    Returns:
        The parsed Job ID string.

    Raises:
        ValueError: If no Job ID could be parsed from the output.
    """
    # Step 1: Extract Job ID from qsub output
    # qsub typically outputs Job ID in format like: "12345.server"
    # or just "12345"

    qsub_output = qsub_output.strip()
    if not qsub_output or '.' not in qsub_output:
        # Some qsub implementations just output the numeric ID
        if qsub_output:
            return qsub_output
        raise ValueError("Could not parse Job ID from qsub output")

    # Step 2: Split and return the job ID
    job_id = qsub_output.split('.')[0]
    return job_id


def submit_and_monitor(args: argparse.Namespace, config: ConfigurationLoader) -> None:
    """Submit a PBS job and start background monitoring.

    Args:
        args: Parsed command line arguments.
        config: The ConfigurationLoader instance.
    """
    # Step 1: Build qsub command with all original arguments
    qsub_cmd = ['qsub'] + args.script + args.qsub_args

    print(f"Submitting job with command: {' '.join(qsub_cmd)}")

    # Step 2: Execute qsub command
    try:
        result = subprocess.run(
            qsub_cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"qsub submission failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Parse Job ID from qsub output
    try:
        job_id = parse_job_id(result.stdout)
        print(f"Job submitted successfully. Job ID: {job_id}")
    except ValueError as e:
        print(f"Failed to parse Job ID: {e}", file=sys.stderr)
        print(f"qsub output: {result.stdout}")
        sys.exit(1)

    # Step 4: Start background monitor process
    print(f"Starting background monitor for job {job_id}...")
    try:
        subprocess.Popen(
            [sys.executable, 'monitor.py', job_id, config.config_path],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"Monitor started. You will receive an email when job {job_id} completes.")
    except Exception as e:
        print(f"Warning: Failed to start monitor: {e}", file=sys.stderr)
        print("Job was submitted but monitoring is not active.")


def main() -> None:
    """Main entry point for mqsub command.

    Parses command line arguments, submits the PBS job,
    and starts monitoring.
    """
    # Step 1: Parse command line arguments
    parser = argparse.ArgumentParser(
        description="PBS job submitter with automatic monitoring and email notification."
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        'script',
        nargs=argparse.REMAINDER,
        help='Script and qsub arguments to pass through'
    )
    parser.add_argument(
        '--qsub-args',
        nargs=argparse.REMAINDER,
        help='Additional qsub arguments'
    )

    args = parser.parse_args()

    # Step 2: Validate that a script was provided
    if not args.script:
        print("Error: No script specified.", file=sys.stderr)
        print("Usage: mqsub <script> [qsub-options...]", file=sys.stderr)
        sys.exit(1)

    # Step 3: Load configuration
    try:
        config = ConfigurationLoader(args.config)
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Submit job and start monitoring
    submit_and_monitor(args, config)


if __name__ == "__main__":
    main()
