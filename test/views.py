# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from media.decorators import use_youtube_api
from media.models import YoutubeVideo


class ListMediaItem(ListView):
    context_object_name = 'media'

    def get_context_data(self, **kwargs):
        context = super(ListMediaItem, self).get_context_data(**kwargs)
        context.update({
            'create_url': 'create_%s' % self.model.__name__.lower(),
            'create_multi_url': 'create_%s_multi' % self.model.__name__.lower(),
            'update_url': 'update_%s' % self.model.__name__.lower(),
            'detail_url': 'detail_%s' % self.model.__name__.lower(),
            'delete_url': 'delete_%s' % self.model.__name__.lower(),
            'detail_multi_url': 'detail_%s_multi' % self.model.__name__.lower(),
            'label': self.model.__name__.upper()
        })
        return context


class CreateMedia(CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateMedia, self).get_context_data(**kwargs)
        context.update({
            'list_url': 'list_%s' % self.model.__name__.lower(),
        })
        return context

    @use_youtube_api(['model'])
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        mock_ct = ContentType.objects.get_for_model(self.request.user)
        self.object = form.save(commit=False)
        self.object.content_type = mock_ct
        self.object.object_pk = self.request.user.pk
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())


# CreateMedia.form_valid = use_youtube_api(CreateMedia.form_valid, models=['model'])


class UpdateMedia(UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateMedia, self).get_context_data(**kwargs)
        context.update({
            'list_url': 'list_%s' % self.model.__name__.lower(),
        })
        return context

    @use_youtube_api(['model'])
    def form_valid(self, form):
        return super(UpdateMedia, self).form_valid(form)


class DetailMedia(DetailView):
    context_object_name = 'media'

    def get_context_data(self, **kwargs):
        context = super(DetailMedia, self).get_context_data(**kwargs)
        context.update({
            'label': self.model.__name__.upper()
        })
        return context


####################################################################################
from django.forms.formsets import formset_factory


class CreateMultipleYoutubeVideos(CreateView):

    def __init__(self, **kwargs):
        super(CreateMultipleYoutubeVideos, self).__init__(**kwargs)
        self.formset = formset_factory(self.form_class, extra=2)

    def get_context_data(self, **kwargs):
        context = super(CreateMultipleYoutubeVideos, self).get_context_data(**kwargs)
        context.update({'formset': self.formset})
        return context

    def post(self, request, *args, **kwargs):
        formset = self.formset(request.POST, request.FILES)

        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    @use_youtube_api(['formset.form.Meta.model'])
    def form_valid(self, formset):
        for form in formset:
            mock_ct = ContentType.objects.get_for_model(self.request.user)
            object = form.save(commit=False)
            object.content_type = mock_ct
            object.object_pk = self.request.user.pk
            object.save()
            form.save_m2m()
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class ShowMultipleYoutubeVideos(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(ShowMultipleYoutubeVideos, self).get_context_data(**kwargs)
        context.update({'youtube_videos': YoutubeVideo.objects.all()})
        return context