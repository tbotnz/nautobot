import time
import uuid

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.test.client import RequestFactory
from django.utils import timezone

from nautobot.extras.choices import LogLevelChoices, JobResultStatusChoices
from nautobot.extras.models import JobLogEntry, JobResult
from nautobot.extras.jobs import get_job, run_job
from nautobot.extras.utils import get_job_content_type
from nautobot.utilities.utils import copy_safe_request


class Command(BaseCommand):
    help = "Run a job (script, report) to validate or update data in Nautobot"

    def add_arguments(self, parser):
        parser.add_argument("job", help="Job to run")
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Commit changes to DB (defaults to dry-run if unset). --username is mandatory if using this argument",
        )
        parser.add_argument(
            "-u",
            "--username",
            help="User account to impersonate as the requester of this job",
        )

    def handle(self, *args, **options):
        if "/" not in options["job"]:
            raise CommandError('Job must be specified in the form "grouping_name/module_name/JobClassName"')
        job_class = get_job(options["job"])
        if not job_class:
            raise CommandError('Job "%s" not found' % options["job"])

        user = None
        request = None
        if options["commit"] and not options["username"]:
            # Job execution with commit=True uses change_logging(), which requires a user as the author of any changes
            raise CommandError("--username is mandatory when --commit is used")

        if options["username"]:
            User = get_user_model()
            try:
                user = User.objects.get(username=options["username"])
            except User.DoesNotExist as exc:
                raise CommandError("No such user") from exc

            request = RequestFactory().request(SERVER_NAME="nautobot_server_runjob")
            request.id = uuid.uuid4()
            request.user = user

        job_content_type = get_job_content_type()

        # Run the job and create a new JobResult
        self.stdout.write("[{:%H:%M:%S}] Running {}...".format(timezone.now(), job_class.class_path))

        job_result = JobResult.enqueue_job(
            run_job,
            job_class.class_path,
            job_content_type,
            user,
            data={},  # TODO: parsing CLI args into a data dictionary is not currently implemented
            request=copy_safe_request(request) if request else None,
            commit=options["commit"],
        )

        # Wait on the job to finish
        while job_result.status not in JobResultStatusChoices.TERMINAL_STATE_CHOICES:
            time.sleep(1)
            job_result = JobResult.objects.get(pk=job_result.pk)

        # Report on success/failure
        groups = set(JobLogEntry.objects.filter(job_result=job_result).values_list("grouping", flat=True))
        for group in sorted(groups):
            logs = JobLogEntry.objects.filter(job_result__pk=job_result.pk, grouping=group)
            success_count = logs.filter(log_level=LogLevelChoices.LOG_SUCCESS).count()
            info_count = logs.filter(log_level=LogLevelChoices.LOG_INFO).count()
            warning_count = logs.filter(log_level=LogLevelChoices.LOG_WARNING).count()
            failure_count = logs.filter(log_level=LogLevelChoices.LOG_FAILURE).count()

            self.stdout.write(
                "\t{}: {} success, {} info, {} warning, {} failure".format(
                    group,
                    success_count,
                    info_count,
                    warning_count,
                    failure_count,
                )
            )

            for log_entry in logs:
                status = log_entry.log_level
                if status == "success":
                    status = self.style.SUCCESS(status)
                elif status == "info":
                    status = status
                elif status == "warning":
                    status = self.style.WARNING(status)
                elif status == "failure":
                    status = self.style.NOTICE(status)

                if log_entry.log_object:
                    self.stdout.write(f"\t\t{status}: {log_entry.log_object}: {log_entry.message}")
                else:
                    self.stdout.write(f"\t\t{status}: {log_entry.message}")

        if job_result.data["output"]:
            self.stdout.write(job_result.data["output"])

        if job_result.status == JobResultStatusChoices.STATUS_FAILED:
            status = self.style.ERROR("FAILED")
        elif job_result.status == JobResultStatusChoices.STATUS_ERRORED:
            status = self.style.ERROR("ERRORED")
        else:
            status = self.style.SUCCESS("SUCCESS")
        self.stdout.write("[{:%H:%M:%S}] {}: {}".format(timezone.now(), job_class.class_path, status))

        # Wrap things up
        self.stdout.write(
            "[{:%H:%M:%S}] {}: Duration {}".format(timezone.now(), job_class.class_path, job_result.duration)
        )
        self.stdout.write("[{:%H:%M:%S}] Finished".format(timezone.now()))
