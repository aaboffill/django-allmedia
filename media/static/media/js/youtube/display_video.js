$(function () {
    var HIDE_IFRAME = 'hide';

    $.initYoutubeVideos = function () {
        var youtubeIFrames = $('.embed-youtube-video'),
        intervalList = [],
        requestingList = [];

        youtubeIFrames.each(function () {
            var $this = $(this),
                url = $this.data('url'),
                hideIFrame = $this.data('whileProcessing') == HIDE_IFRAME,
                whileProcessingInfo = ($this.data('whileProcessingInfo') != undefined) ? $($this.data('whileProcessingInfo')) : null,
                processed = ($this.data('processed') != undefined) ? $this.data('processed') == "1" : false;

            if (!processed && url != undefined) {
                if (hideIFrame) $this.hide();
                if (whileProcessingInfo) whileProcessingInfo.show();

                requestingList[url] = false;
                intervalList[url] = window.setInterval(function() {
                    if (!requestingList[url]) {
                        requestingList[url] = true;
                        $.get(url, function (response) {
                            if (response['result']) {
                                if (response['processed']) {
                                    window.clearInterval(intervalList[url]);
                                    $this.show();
                                    whileProcessingInfo.hide();
                                }
                            } else {
                                $.each(response['failedMsgs'], function (i, msg) {
                                    if (typeof $.addNotification != 'undefined') {
                                        $.addNotification($.TOP_LAYOUT, $.ERROR, msg);
                                    } else {
                                        alert(msg);
                                    }
                                });
                            }
                        }).complete(function () {
                            requestingList[url] = false;
                        });
                    }
                }, 60000);
            }
        });
    };

    $.initYoutubeVideos();

});