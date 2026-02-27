# PBS Job Monitor & Notifier

A command-line tool that wraps the PBS `qsub` command and automatically monitors job status, sending email notifications when jobs complete.

## Features

- Transparent wrapper around `qsub` - all `qsub` options are passed through
- Automatic background monitoring of submitted jobs
- Email notifications when jobs complete
- Configurable polling intervals
- Easy configuration via JSON file

## Installation

No installation required. Just ensure you have Python 3.6+ installed.

```bash
git clone <repository-url>
cd CCMGpbs_auto_monitor
```

## Configuration

1. Copy the example configuration file:

```bash
cp config.json.example config.json
```

2. Edit `config.json` with your settings:

```json
{
  "pbs_username": "zpzheng",
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "smtp_user": "your_email@example.com",
  "smtp_password": "your_password_or_app_token",
  "recipient_email": "recipient@example.com",
  "poll_interval": 60
}
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `pbs_username` | PBS system username | No | `zpzheng` |
| `smtp_server` | SMTP server address | Yes | - |
| `smtp_port` | SMTP port number | Yes | - |
| `smtp_user` | Email address for SMTP login | Yes | - |
| `smtp_password` | SMTP password or app token | Yes | - |
| `recipient_email` | Email to receive notifications | Yes | - |
| `poll_interval` | Polling interval in seconds | No | `60` |

## Usage

Submit a PBS job with automatic monitoring:

```bash
python mqsub.py script.sh -l nodes=1:ppn=4 -q share -N myjob
```

All standard `qsub` options are supported:

```bash
python mqsub.py XX.sh -l nodes=x:ppn=xx -q xxx -N xxx
```

### Command Options

- `-c, --config FILE`: Path to configuration file (default: `config.json`)
- `-h, --help`: Show help message

### How It Works

1. `mqsub` wraps the `qsub` command and submits your job
2. The Job ID is parsed from `qsub` output
3. A background monitor process is started
4. The monitor polls `qstat` at configured intervals
5. When the job completes (status `C` or removed from queue), an email notification is sent

## Architecture

```
CCMGpbs_auto_monitor/
├── __init__.py           # Package initialization
├── config_loader.py      # Configuration loading and validation
├── notifier.py           # Email notification handler
├── monitor.py            # Job status monitor
├── mqsub.py              # Main CLI entry point
├── config.json.example   # Configuration template
└── README.md             # This file
```

## Requirements

- Python 3.6+
- PBS/Torque job scheduler (`qsub`, `qstat`, `tracejob`)
- SMTP server access (e.g., Gmail, Outlook, or corporate SMTP)

## Module Documentation

All modules follow Google Style Python Docstrings.

### ConfigurationLoader (`config_loader.py`)

Loads and validates configuration from JSON file.

### EmailNotifier (`notifier.py`)

Handles SMTP email notifications for job completion.

### JobMonitor (`monitor.py`)

Monitors PBS job status using `qstat` and triggers notifications.

## Troubleshooting

### Monitoring not starting

- Ensure `config.json` exists and is valid
- Check that all required parameters are configured
- Verify SMTP credentials are correct

### Job not found error

- The job may have already completed or failed before monitoring started
- Check the job submission output for the Job ID

### Email not received

- Check spam/junk folders
- Verify SMTP server settings (address, port)
- Confirm email authentication credentials
- Some providers require app-specific passwords (e.g., Gmail)
