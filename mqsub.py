""" Main entry point for PBS Job Monitor & Notifier.

This script wraps the qsub command and starts a background monitor
for the submitted job.
"""

import subprocess
import sys
from config_loader import ConfigurationLoader


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

    if not qsub_output:
        raise ValueError("qsub output is empty")

    # Step 2: Split and return the job ID (remove server suffix)
    parts = qsub_output.split('.')
    return parts[0]


def submit_and_monitor(qsub_args: list, config: ConfigurationLoader) -> None:
    """Submit a PBS job and start background monitoring.

    Args:
        qsub_args: List of arguments to pass to qsub (excluding qsub itself).
        config: The ConfigurationLoader instance.
    """
    # Step 1: Build qsub command with all arguments
    qsub_cmd = ['qsub'] + qsub_args

    print(f"Submitting job with command: {' '.join(qsub_cmd)}")
    print("Note: If PBS requires authentication, you may be prompted for a password below.")

    # Step 2: Execute qsub command with stdin connected for password input
    try:
        result = subprocess.run(
            qsub_cmd,
            stdin=None,  # Connect to parent stdin for password input
            stdout=subprocess.PIPE,  # Capture stdout to parse Job ID
            stderr=subprocess.PIPE,  # Capture stderr
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"qsub submission failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: qsub command not found. PBS/Torque may not be installed.", file=sys.stderr)
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
        # Step 4.1: Use nohup to ensure process continues after terminal closes
        nohup_cmd = [
            'nohup',
            sys.executable,
            'monitor.py',
            job_id,
            config.config_path
        ]
        subprocess.Popen(
            nohup_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        print(f"Monitor started. You will receive an email when job {job_id} completes.")
        print("Monitor will continue running even if you close this terminal.")
    except Exception as e:
        print(f"Warning: Failed to start monitor: {e}", file=sys.stderr)
        print("Job was submitted but monitoring is not active.")


def main() -> None:
    """Main entry point for mqsub command.

    Parses command line arguments, submits the PBS job,
    and starts monitoring.
    """
    # Step 1: Parse only our own arguments and pass the rest to qsub
    config_path = 'config.json'
    qsub_args = []

    i = 1  # Skip script name (argv[0])
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('-c', '--config'):
            # Step 2: Handle config argument
            if i + 1 >= len(sys.argv):
                print("Error: --config requires a value", file=sys.stderr)
                sys.exit(1)
            config_path = sys.argv[i + 1]
            i += 2
        elif arg == '--help' or arg == '-h':
            # Step 3: Handle help argument
            print("Usage: mqsub [MQSUB_OPTIONS] [QSUB_OPTIONS]")
            print()
            print("MQSUB_OPTIONS:")
            print("  -c, --config FILE    Path to configuration file (default: config.json)")
            print("  -h, --help           Show this help message")
            print()
            print("QSUB_OPTIONS:")
            print("  All other options are passed directly to qsub.")
            print("  Example: mqsub XX.sh -l nodes=1:ppn=4 -q share -N myjob")
            print()
            print("To see qsub options, run: qsub --help")
            sys.exit(0)
        else:
            # Step 4: Pass remaining arguments to qsub
            qsub_args.append(arg)
            i += 1

    # Step 5: Validate that at least one argument was provided for qsub
    if not qsub_args:
        print("Error: No script specified.", file=sys.stderr)
        print("Usage: mqsub <script> [qsub-options...]", file=sys.stderr)
        print("Run: mqsub --help for more information")
        sys.exit(1)

    # Step 6: Load configuration
    try:
        config = ConfigurationLoader(config_path)
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 7: Submit job and start monitoring
    submit_and_monitor(qsub_args, config)


if __name__ == "__main__":
    main()
