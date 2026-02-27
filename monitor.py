""" Job monitor module for PBS Job Monitor & Notifier.

This module handles monitoring PBS job status and triggering notifications.
"""

import subprocess
import time
import sys
from typing import Optional, Tuple
from config_loader import ConfigurationLoader
from notifier import EmailNotifier


class JobMonitor:
    """Monitors PBS jobs and sends notifications on completion.

    This class periodically checks the status of a PBS job using qstat
    and sends an email notification when the job completes.
    """

    def __init__(self, config: ConfigurationLoader):
        """Initialize the JobMonitor with configuration.

        Args:
            config: The ConfigurationLoader instance.
        """
        # Step 1: Store configuration
        self.config = config

        # Step 2: Initialize email notifier
        self.notifier = EmailNotifier(
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port,
            smtp_user=config.smtp_user,
            smtp_password=config.smtp_password
        )

    def monitor_job(self, job_id: str) -> None:
        """Monitor a PBS job until completion and send notification.

        Args:
            job_id: The PBS job ID to monitor.
        """
        # Step 1: Verify job is in queue before monitoring
        job_name, initial_status = self._get_job_status(job_id)
        job_enqueued = initial_status is not None

        # Step 2: If job was never found in queue, exit early
        if not job_enqueued:
            print(f"Job {job_id} not found in queue, exiting monitor.")
            return

        # Step 3: Start monitoring loop
        print(f"Monitoring job {job_id}...")
        while True:
            # Step 4: Periodically check job status
            job_name, status = self._get_job_status(job_id)

            # Step 5: Check completion conditions:
            # - Job status is 'C' (Completed)
            # - Job was enqueued and now cannot be found (removed from queue)
            if status == 'C' or (job_enqueued and status is None):
                exit_status = self._get_exit_status(job_id)
                self._send_notification(job_id, job_name, exit_status)
                break

            # Step 6: Job is pending/running, continue monitoring
            # Step 7: Wait for next polling interval
            time.sleep(self.config.poll_interval)

    def _get_job_status(self, job_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Get the current status of a PBS job.

        Args:
            job_id: The PBS job ID to check.

        Returns:
            A tuple of (job_name, status) where job_name is the job name
            and status is the job status code. Returns (None, None) if job not found.
        """
        # Step 1: Execute qstat command to get job info
        try:
            result = subprocess.run(
                ['qstat', '-f', job_id],
                capture_output=True,
                text=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            return None, None
        except Exception:
            return None, None

        # Step 2: Parse job status from output
        job_name = self._parse_job_name(result.stdout)
        status = self._parse_job_status(result.stdout)

        return job_name, status

    def _parse_job_name(self, output: str) -> Optional[str]:
        """Parse job name from qstat output.

        Args:
            output: The stdout from qstat -f command.

        Returns:
            The job name, or None if not found.
        """
        # Step 1: Search for Job_Name in output
        for line in output.split('\n'):
            if line.strip().startswith('Job_Name = '):
                return line.split('=', 1)[1].strip().strip('"')
        return None

    def _parse_job_status(self, output: str) -> Optional[str]:
        """Parse job status from qstat output.

        Args:
            output: The stdout from qstat -f command.

        Returns:
            The job status code, or None if not found.
        """
        # Step 1: Search for job_state in output
        for line in output.split('\n'):
            if line.strip().startswith('job_state = '):
                return line.split('=', 1)[1].strip().strip('"')

        # Step 2: If no status found, job may have exited
        return None

    def _get_exit_status(self, job_id: str) -> Optional[str]:
        """Get the exit status of a completed job.

        Args:
            job_id: The PBS job ID.

        Returns:
            The exit status string, or None if not available.
        """
        # Step 1: Try to get exit status from tracejob
        try:
            result = subprocess.run(
                ['tracejob', '-n', '1', job_id],
                capture_output=True,
                text=True,
                timeout=30
            )
        except Exception:
            return None

        # Step 2: Parse exit status from tracejob output
        if 'Exit_status' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'Exit_status' in line:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        return parts[2]
        return None

    def _send_notification(self, job_id: str, job_name: Optional[str],
                           exit_status: Optional[str]) -> None:
        """Send email notification for job completion.

        Args:
            job_id: The PBS job ID.
            job_name: The job name.
            exit_status: The exit status of the job.
        """
        # Step 1: Send the email notification
        success = self.notifier.send_notification(
            recipient_email=self.config.recipient_email,
            job_id=job_id,
            job_name=job_name,
            exit_status=exit_status
        )

        # Step 2: Log result
        if success:
            print(f"Notification sent for job {job_id}")
        else:
            print(f"Failed to send notification for job {job_id}")


def main(job_id: str, config_path: str = "config.json") -> None:
    """Entry point for the monitor subprocess.

    This function is called when the monitor runs as a separate process.

    Args:
        job_id: The PBS job ID to monitor.
        config_path: Path to the configuration file.
    """
    # Step 1: Load configuration
    config = ConfigurationLoader(config_path)

    # Step 2: Initialize and run monitor
    monitor = JobMonitor(config)
    monitor.monitor_job(job_id)


if __name__ == "__main__":
    # Step 1: Get job_id from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <job_id> [config_path]")
        sys.exit(1)

    job_id_arg = sys.argv[1]
    config_path_arg = sys.argv[2] if len(sys.argv) > 2 else "config.json"

    # Step 2: Run monitor
    main(job_id_arg, config_path_arg)
