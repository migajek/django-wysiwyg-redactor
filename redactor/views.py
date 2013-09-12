import os

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from sorl.thumbnail import get_thumbnail
from redactor.forms import ImageForm
import json


UPLOAD_PATH = getattr(settings, 'REDACTOR_UPLOAD', 'redactor/')
BROWSE_FOLDERS = getattr(settings, 'REDACTOR_BROWSE_FOLDERS', {'Default': UPLOAD_PATH})

@csrf_exempt
@require_POST
@login_required
def redactor_upload(request, upload_to=None, form_class=ImageForm, response=lambda name, url: url):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']
        path = os.path.join(upload_to or UPLOAD_PATH, file_.name)
        real_path = default_storage.save(path, file_)
        return HttpResponse(
            response(file_.name, os.path.join(settings.MEDIA_URL, real_path))
        )
    return HttpResponse(status=403)


def browse_images(request):
    result = []    
    for fname, folder in BROWSE_FOLDERS.items():
        files = [(os.path.join(folder, x), x) for x in default_storage.listdir(folder)[1]]
        result += [ {'image': default_storage.url(x[0]), 
               'title': x[1],
               'thumb': get_thumbnail(x[0], '150x150', upscale = False).url,
               'folder': fname,
               } for x in files]
            
    return HttpResponse(content_type = 'text/javascript', content = json.dumps(result))