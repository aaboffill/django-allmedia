# coding=utf-8
from django.utils.encoding import force_text
from django.views.generic import View, TemplateView
from django.utils.translation import ugettext_lazy as _
from .forms import AjaxFileUploadedForm
from .models import YoutubeVideo, YoutubeUploadProgress
from .mixins import JSONResponseMixin


class HandleAjaxFileUploadedView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            content = request.POST.get('content', "all")
            form = AjaxFileUploadedForm(request.POST, request.FILES, content=content)
            if form.is_valid():
                model = form.save()

                return self.render_to_response({
                    'result': True,
                    'object_pk': model.pk
                })

            messages = {}
            for i in xrange(len(form.errors)):
                item_error_list = form.errors.items()[i][1]
                for j in xrange(len(item_error_list)):
                    messages.update({j: force_text(item_error_list[j])})

            return self.render_to_response({
                'result': False,
                'failedMsgs': messages
            })

        except Exception as e:
            return self.render_to_response({
                'result': False,
                'failedMsgs': {1: force_text(_(u"A problem has occurred while trying to save the uploaded file."))}
            })


class HandleYoutubeProcessingView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        video_id = kwargs['video_id']
        try:
            video = YoutubeVideo.objects.get(pk=video_id)
            processing_progress = video.file.processing_progress

            return self.render_to_response({
                'result': True,
                'processing_progress': processing_progress
            })

        except YoutubeVideo.DoesNotExist:
            return self.render_to_response({
                'result': False,
                'failedMsgs': {1: force_text(_(u"The video specified with id:%s does not exist.") % video_id)}
            })


class YoutubeUploadProcessView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(YoutubeUploadProcessView, self).get_context_data(**kwargs)
        try:
            progress = YoutubeUploadProgress.objects.get(session_key=self.request.session.session_key)
            context.update({'youtube_upload_status': progress.progress_data})
        except YoutubeUploadProgress.DoesNotExist:
            pass
        return context

