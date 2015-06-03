==========================
Django AllMedia
==========================

All Media for Django>=1.6.1

Images, Videos, Attachments. All of them can be related to any django model instance (through generic foreign key).
Image and Video tagging support.
Image thumbnail processing.

Changelog
=========
1.0.9
-----

Added setting to specify an specific oauth2 authentication port.

1.0.8
-----

Added loggers for the youtube service oauth authentication.

1.0.7
-----

Fixed youtube data actualization.

1.0.6
-----

Changed support for youtube upload progress management to cache or DB. Added decorators to manage the ajax file upload
to generic and inline django formsets.

1.0.5
-----

Added a model to manage the youtube upload progress using the request session key. Added support for ajax upload
file for django formset.

1.0.3
-----

Deleted connect_signals method call from the media init file.

1.0.2
-----

Added support for several videos processed simultaneously.


1.0.1
-----

Testing and fixing problems using youtube django storage backend, this time through django administration.


1.0.0
-----

Refactoring all media models. Added implementation of youtube as video storage backend.
Added convert_filename method in utils, to remove non ascii characters and to transform white spaces to underscores.


0.3.5
-----

Fixes for compatibility with Django 1.8.


0.3.4
-----

Fix in 'upload-to' configuration usage for docs.


0.3.3
-----

Allowed 'upload-to' configuration for media and docs.


0.3.2
-----

Calling form method save_m2m to fix bug.
Implemented form class AttachmentAjaxUploadForm

0.3.1
-----

Allow decorated model forms to have additional kwargs (besides 'commit') if overwritten.

0.3.0
-----

Support for file validations by js and django

0.2.1
-----

Support for on demand thumbnail generation (if indicated by settings)

0.2.0
-----

Support for ajax file uploads

0.1.0
-----

PENDING...

Notes
-----

PENDING...

Usage
-----

1. Run ``python setup.py install`` to install.

2. Modify your Django settings to use ``media``:

3. Make sure you have compiled and installed PIL with support for jpeg.

4. Setup your thumbs generation process (optional)
    Example:

    In django settings:

    MEDIA_THUMBNAIL_SIZES =  {
        'usage_1': [('51x51', 'scale'), ('392x392', 'scale'), ('60x60', 'crop'), ('74x74', 'crop'), ('64x64', 'crop')],
        'usage_2': [('392x392', 'scale'), ('150x150', 'scale'), ('500x500', 'scale'), ('267x200', 'scale')],
    }

    In code:
    When u need to execute the thumbs generation, just call the create_thumbnails function (passing in the image_path and usage params).
    This may be done either in synchronous or asynchronous way (as a celery task).

5. Optionally upload django ``FileField`` by ajax, once the file is included, in order to avoid submit several files at the same
    time and avoid a possible connection timeout.

    If you want to use (Ajax Upload and File Validations), you also need to use bootstrap fileinput js component and jQuery.

    -- Include the ``ajax_file_upload`` decorator for each django model form that contains files that you need to upload
    by ajax. You can specify the following args:

        - ``form_file_field_name`` : The file field name inside the form.

        - ``model_file_field_name`` : The file field name inside the model related with the form, if this arg is not defined
          then is assumed to be the same as the ``form_file_field_name``.

        - ``content_type`` : The content type related with file field. This content type is used to validate size and type.

          Example: ``image``, ``video``, ``docs``, and the sum of all content types as ``all``
            You can see the content types definitions and overwrite them using the setting ``MEDIA_STATICFILES_FORMATS``

    -- To complement this behavior you should include ``ajax_upload.js`` and define the following structure in the template.

        - ``simple-ajax-upload`` : Add this class to the fileinput main div.

        - ``data-url`` : Add this data attribute to the file input, to specify the url to make the ajax upload request.

        - ``data-validation`` : Add this data attribute to the file input, to specify the name of the validation method
          that will be evaluated (optional).

        - ``data-closestcontainer`` : Add this data attribute to the file input, to specify the selector for the parent container.

        - ``data-progresscontainer`` : Add this data attribute to the file input, to specify the selector for the progress bar container.

          If ``data-closestcontainer`` is not defined but ``data-progresscontainer`` is defined, then the ``data-progresscontainer``
            will be used as ``data-closestcontainer`` too.

        - ``data-contentvalidation`` : Add this data attribute to the file input, to specify the content type format and
          validate size and type.
          If this value is not specified, ``all`` will be assumed.

        - ``temp_file_id`` : Add a temporal file input for ajax purposes.

          Example:

          <div class="file-container">
            <div class="fileinput simple-ajax-upload fileinput-{% if form.instance.pk and form.instance.file.url %}exists{% else %}new{% endif %}" data-provides="fileinput">
                {% if form.instance.pk and form.instance.file.url %}<input type="hidden" value="" name="">{% endif %}
                <div>
                    <div><span class="fileinput-preview">{% if form.instance.pk and form.instance.file.url %}{{ form.instance.file.url }}{% endif %}</span></div>
                    <span class="input-group-btn">
                        <span class="btn-file">
                            <span class="fileinput-new">Select File</span>
                            <span class="fileinput-exists">Change File</span>
                            {% url "ajax_upload_file" as ajax_upload_file_url %}
                            {% render_field form.file data-url=ajax_upload_file_url data-progresscontainer=".file-container" %}
                            {% render_field form.temp_file_id %}
                        </span> </br>
                        <a href="#" class="fileinput-exists" data-dismiss="fileinput">Clean or Change</a>
                    </span>
                </div>
            </div>
        </div>

6. Use youtube as video storage backend (optional)

    -- To use this functionality you must follow the next steps:
        - If you don't already have a Google account, sign up(https://www.google.com/accounts).
        - If you have never created a Google APIs Console project, read the Managing Projects page(https://developers.google.com/console/help/managing-projects)
          and create a project in the Google Developers Console(https://console.developers.google.com/).
        - After project creation, select the youtube API data as a new service for your project:
            + Go to the console API(https://console.developers.google.com/project) and select the project that you have just created.
            + Click in the API service panel.
            + In the API list, search and select the youtube API V3 and change the state to ON.
        - Read the Google API Client Library for Python(https://developers.google.com/api-client-library/python/guide/aaa_oauth) to learn about OAuth 2.0
        authentication and how acquire the client IDs.

    -- Settings:

        + ``YOUTUBE_CONF_FOLDER`` : Base path to the youtube configuration folder.

        + ``YOUTUBE_CLIENT_SECRETS_FILE`` : Client secret json file name. This path store oauth authentication data.
          This file must be saved inside the youtube configuration folder, the full path should be the concatenation of
          ``YOUTUBE_CONF_FOLDER`` and ``YOUTUBE_CLIENT_SECRETS_FILE``.

        + ``YOUTUBE_DEFAULT_PRIVACY_STATUS`` : This setting define the default behavior of the youtube privacy status (optional).
          Possible values:
            ("public", "private", "unlisted") or (0, 1, 2) respectively

        + ``YOUTUBE_DEFAULT_CATEGORY`` : The default youtube category for the uploaded videos (optional).
          By default is 22, you can read more about youtube video categories(https://developers.google.com/youtube/v3/docs/videoCategories).

        + ``YOUTUBE_BASE_URL`` : Define the youtube url that will be embedded in the page (optional).
          By default is ``http://www.youtube.com/embed/%s``, but you can override it and add params un the youtube url.

          Example: ``http://www.youtube.com/embed/%s?autoplay=1&controls=1&loop=0``

          Note that the param '%s' will be replaced by the youtube video key.

        + ``YOUTUBE_UPLOAD_CHUNK_SIZE`` : Specify the chunk size for uploading the video (optional).
          It's important to specify a value if you wish to show the youtube upload progress to the user. If the specified value is not divisible by 256,
          an error will be raised.

        + ``YOUTUBE_SPECIFIC_AUTH_PORT`` : If is necessary you can specify the port that you pretend use to the oauth2 authentication.

    -- Usage:
        + Replace the django ``FileField`` for the subclass ``YoutubeFileField`` to define the video file field in the model. For the ``YoutubeFileField``
        you can optionally specify the title, privacy, comment and tags for the youtube video.
        Example:

        class YoutubeVideo(Media):

            file = YoutubeFileField(
                _('youtube_file'),
                upload_to=Media.upload_to, # Set the FileField mandatory ``upload_to`` argument to any value, it won't be used anyway.
                max_length=255,
                privacy=False,
                comment=Media.description,
                tags=Media.tag_list
            )

        + If you wish show the upload progress to the user, you need to include the ``show_youtube_upload_process`` decorator to the corresponding view,
          and to include the ``show_upload_process.js`` in the template.

        The ``show_youtube_upload_process`` decorator have the following args:

          - ``fields`` : Specify the youtube fields that you wish to show uploading progress for, if you don't specify any field, progress for all youtube
            fields will be shown.

          - ``model`` : Specify the model corresponding to the view, if don't specify it, the decorator will assume that the view is a subclass of ``CreateView``
            or ``UpdateView`` and the model will be took from the view's model attribute.

          - ``save_method`` : Specify the method where the model instance will be saved, if don't specify it, the decorator will assume that the view
            is a subclass of ``CreateView`` or ``UpdateView`` and that the method is the ``form_valid`` method of the view.

        To ensure that the upload progress is shown successfully, you must to add the class ``youtube-files`` to the corresponding HTML form, also you need to specify
          the following form data:

          - ``data-youtube-process-url`` : Define the url that will be requested to retrieve the progress information.

          - ``data-youtube-process-parent`` : Specify the HTML container where will be append the youtube processing information.


        + When you upload a video to youtube, youtube begins processing the file, this process could take several minutes. During this
         period, if you access the video for displaying, it won't be reproduced. In order to inform to the user of the progress of this process, you can use the
         ``display_video.html`` to show the youtube player and to show the processing progress. You need to include ``display_video.js`` in the template.

         You can optionally overwrite the ``display_video.html`` template. By default, this template show the progress using an HTML progress bar,
         but you can use other progress bar implementation like bootstrap progress bar if you respect the following principles:

            In the youtube embedded ``iframe``, you need to add a class named ``embed-youtube-video`` and to define some data attributes to guarantee a success
            progress display:

            - ``data-while-processing`` : Set to "hide" or "show" whether you want to hide the youtube player while the video is still in process or not.
              Example: (data-while-processing="hide" or data-while-processing="show")

            - ``data-url`` : Define the url that will be requested to retrieve the progress information.

            - ``data-progress-container`` : Represents the HTML container of the progress HTML information.

            - ``data-processing-percent`` : Specify the percent value container.
            - ``data-processing-time-left`` : Specify the remaining time value container.
            - ``data-processing-processed`` : Specify the processed value container.
            - ``data-processing-total`` : Specify the total value container.
            - ``data-video-status`` : Specify the status value container.

            The last 5 data attributes, need to match the following format:

              'html_selector:(func|attr)->name_of_func_or_attr' where:
               ``func`` represent a method of the HTML component that will be called to set the value, as (.value(), text(), ...)
               ``attr`` represent an attribute of the HTML component where will be setted the value, as (value="", max="", ...)

              Example:
              data-processing-percent="#youtube-processing-percent:func->text"
              data-processing-time-left="#youtube-processing-time-left:func->text"
              data-processing-processed="#youtube-processing-progress:attr->value"
              data-processing-total="#youtube-processing-progress:attr->max"
              data-video-status="#video-status:func->text"
