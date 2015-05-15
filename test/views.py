# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from media.decorators import show_youtube_upload_process


class ListMediaItem(ListView):
    context_object_name = 'media'

    def get_context_data(self, **kwargs):
        context = super(ListMediaItem, self).get_context_data(**kwargs)
        context.update({
            'create_url': 'create_%s' % self.model.__name__.lower(),
            'update_url': 'update_%s' % self.model.__name__.lower(),
            'detail_url': 'detail_%s' % self.model.__name__.lower(),
            'delete_url': 'delete_%s' % self.model.__name__.lower(),
            'label': self.model.__name__.upper()
        })
        return context


@show_youtube_upload_process()
class CreateMedia(CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateMedia, self).get_context_data(**kwargs)
        context.update({
            'list_url': 'list_%s' % self.model.__name__.lower(),
        })
        return context

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


@show_youtube_upload_process()
class UpdateMedia(UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateMedia, self).get_context_data(**kwargs)
        context.update({
            'list_url': 'list_%s' % self.model.__name__.lower(),
        })
        return context


class DetailMedia(DetailView):
    context_object_name = 'media'

    def get_context_data(self, **kwargs):
        context = super(DetailMedia, self).get_context_data(**kwargs)
        context.update({
            'label': self.model.__name__.upper()
        })
        return context