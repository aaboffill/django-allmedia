$(function () {
    var youtubeFileForms = $('form.youtube-files');

    youtubeFileForms.each(function() {
        var $this = $(this),
            youtubeFilesCount = (typeof $this.data('youtubeFilesCount') != 'undefined') ? $this.data('youtubeFilesCount') : null,
            youtubeUploadProcessParent = (typeof $($this.data('youtubeProcessParent')) != 'undefined') ? $($this.data('youtubeProcessParent')) : null,
            youtubeProcessUrl = (typeof $this.data('youtubeProcessUrl') != 'undefined') ? $this.data('youtubeProcessUrl') : null;

        if (youtubeFilesCount == null) throw new Error('The youtube files count data must be specified.');

        if (!parseInt(youtubeFilesCount)) {
            var errorMsg = 'The youtube files count value must be an integer val or a function name.';

            if (!$.isFunction(eval(youtubeFilesCount))) throw new Error(errorMsg);

            youtubeFilesCount = eval(eval(youtubeFilesCount))();

            if (!parseInt(youtubeFilesCount)) throw new Error(errorMsg);

        }

        if (youtubeUploadProcessParent == null) throw new Error('The youtube upload process parent data must be specified.');

        if (youtubeProcessUrl == null) throw new Error('The youtube process url data must be specified.');


        $this.on('submit', function () {
            var requesting = false,
                interval = window.setInterval(function () {
                    if (!requesting) {
                        requesting = !requesting;
                        $.get(youtubeProcessUrl, function (response, status) {
                            if (status == 'success') {
                                youtubeUploadProcessParent.html(response);

                                // Throw a success event to add another behavior
                                $this.trigger($.Event('success.youtubeChunk.processed'));
                            } else {
                                // Throw a fail event to add another behavior
                                $this.trigger($.Event('fail.youtubeChunk.processed'));
                            }
                        }, 'html').fail(function () {
                            // Throw a fail event to add another behavior
                            $this.trigger($.Event('fail.youtubeChunk.processed'));
                        }).complete(function () {
                            requesting = !requesting;
                        });
                    }
                }, 3000);
        });
    });
});