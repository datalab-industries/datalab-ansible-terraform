# Emails for failed cron jobs

The playbook schedules several cron jobs as the docker user: certificate renewal, weekly snapshots, Borg backups and ChemInventory syncing.
Each job writes its output to `~/last_<job>.txt` and only prints it if the job fails.
Cron then emails that output to the `MAILTO` address.

This is separate from the SMTP settings that *datalab* itself uses for email login.
You can use the same SMTP provider for both.

## Setup

1. Get SMTP credentials, e.g., from [Resend](https://resend.com/docs/send-with-smtp), and verify the sender domain with the provider.
2. Add the settings to your inventory:
   ```yaml
   cron_mailto: <the address to email failed cron jobs to>
   cron_mail_from: <the sender address, on a domain verified with the SMTP provider>
   cron_smtp_host: smtp.resend.com
   cron_smtp_user: resend
   cron_smtp_password: <your Resend API key>
   cron_smtp_port: 587  # optional; the default
   ```
   All settings except `cron_smtp_port` must be set together.
   Setting only some of them fails the playbook run.
   Port 465 uses implicit TLS; any other port uses STARTTLS.
3. Run the playbook with the `cron_email` tag:
   ```shell
   make cron_email
   ```

A test email is sent whenever the SMTP settings or addresses change.

## How it works

On Debian and Ubuntu, the role installs [msmtp](https://marlam.de/msmtp/) as the system `sendmail`, configures it for the docker user, and sets `MAILTO` in their crontab.

msmtp is not installed if the host already runs a mail server (e.g., postfix), or if the system is not managed by the playbook (`manage_system: false`).
In those cases, the existing `sendmail` is used.

## Alerting with PagerDuty or similar

Failures can also raise incidents in an alerting service that accepts inbound email, such as [PagerDuty](https://support.pagerduty.com/main/docs/email-integration-guide).

Add an **Email** integration to a PagerDuty service, and add its address to `cron_mailto`.
Multiple addresses can be separated by commas:

```yaml
cron_mailto: "team@example.com,datalab-cron@yourorg.pagerduty.com"
```

The email subject names the host and the job.
Configure the integration to open a new incident only if one is not already open for the same subject.
Otherwise, each repeated failure opens a new incident.

Note that:

- incidents are not resolved automatically when a job next succeeds,
- the test email sent when the settings change will also raise an incident.
