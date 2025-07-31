import glob
import os
import time
import redis

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser


class Command(BaseCommand):
    help = "Store React build filenames in Redis cache"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait for build files to be available",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout in seconds for waiting (default: 300)",
        )

    def handle(self, *args: tuple, **options: dict) -> None:
        """Store the current React build filenames in Redis"""
        try:
            # Connect to Redis
            r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

            # Find the built files
            staticfiles_dir = "/build/react/assets"

            # Wait for files if requested
            if options.get("wait"):
                self.stdout.write("⏳ Waiting for React build files...")
                start_time = time.time()
                timeout = options.get("timeout", 300)
                if not isinstance(timeout, int):
                    timeout = 300

                while time.time() - start_time < timeout:
                    js_files = glob.glob(f"{staticfiles_dir}/index-*.js")
                    css_files = glob.glob(f"{staticfiles_dir}/index-*.css")

                    if js_files and css_files:
                        self.stdout.write("✅ Build files found!")
                        break

                    self.stdout.write("⏳ Still waiting for build files...")
                    time.sleep(5)
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Timeout waiting for build files after {timeout} seconds"
                        )
                    )
                    return

            # Find JS file
            js_files = glob.glob(f"{staticfiles_dir}/index-*.js")
            if js_files:
                js_filename = os.path.basename(js_files[0])
                r.set("react:js_file", js_filename)
                self.stdout.write(self.style.SUCCESS(f"✅ Stored JS file: {js_filename}"))
            else:
                self.stdout.write(self.style.WARNING("❌ No JS file found"))

            # Find CSS file
            css_files = glob.glob(f"{staticfiles_dir}/index-*.css")
            if css_files:
                css_filename = os.path.basename(css_files[0])
                r.set("react:css_file", css_filename)
                self.stdout.write(self.style.SUCCESS(f"✅ Stored CSS file: {css_filename}"))
            else:
                self.stdout.write(self.style.WARNING("❌ No CSS file found"))

            self.stdout.write(self.style.SUCCESS("✅ Build files stored in Redis cache"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error storing build files: {e}"))
            raise
