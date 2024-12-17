from django.core.management import BaseCommand
import helpers
from django.conf import settings

OUT_DIR = getattr(settings,'STATICFILES_VENDORS_DIR')

VENDOR_FILES = {
    "flowbite.min.css":"https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.css",
     "flowbite.min.js":"https://cdn.jsdelivr.net/npm/flowbite@2.5.2/dist/flowbite.min.js"
}

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Downloading vendor files!")
        for name,url in VENDOR_FILES.items():
            print(name,url)
            out_path = OUT_DIR / name
            success = helpers.download_to_local(url, out_path)
            if success:
                self.stdout.write(self.style.SUCCESS(f"Completed : {out_path}"))
            else:
                self.stdout.write(self.style.WARNING(f"Failed : {out_path}"))

