$(function () {
    var ATTRIBUTE = 'attr',
        HIDE_IFRAME = 'hide',
        requesting = false,
        valueFromData = function(expression, value) {
            if (typeof expression == 'undefined') throw new Error('The param "expression" must be specified.');

            // elements[0] = html selector, elements[1] = localization inside the html element and value
            var elements = expression.split(':', 2);
            if (elements.length != 2) throw new Error('Expected two elements separated by ":" in the param "expression".');

            // localization[0] = localization inside the html element, localization[1] = value
            var localization = elements[1].split('->', 2);
            if (localization.length != 2) throw new Error('Expected two elements separated by "->" in "elements[1]".');

            if (value == null)
                return (localization[0] == ATTRIBUTE) ? $(elements[0]).attr(localization[1]) : eval('$(elements[0]).' + localization[1] + '()');
            else
                return (localization[0] == ATTRIBUTE) ? $(elements[0]).attr(localization[1], value) : eval('$(elements[0]).' + localization[1] + '(\'' + value +'\')');
        },
        youtubeIFrame = $('#embed-youtube-video'),
        processingPercent = valueFromData(youtubeIFrame.data('processingPercent'), null),
        interval = null;

    if (parseInt(processingPercent) != 100) {
        var url = youtubeIFrame.data('url'),
            hideIFrame = youtubeIFrame.data('whileProcessing') == HIDE_IFRAME;

        if (typeof url != 'undefined') {
            if (hideIFrame) youtubeIFrame.hide();

            interval = window.setInterval(function() {
                if (!requesting) {
                    requesting = !requesting;
                    $.get(url, function (response) {
                        if (response['result']) {
                            processingPercent = response['processing_progress']['percent'];
                            valueFromData(youtubeIFrame.data('processingPercent'), processingPercent);
                            valueFromData(youtubeIFrame.data('processingTimeLeft'), response['processing_progress']['time_left_ms']);
                            valueFromData(youtubeIFrame.data('processingProcessed'), response['processing_progress']['parts_processed']);
                            valueFromData(youtubeIFrame.data('processingTotal'), response['processing_progress']['parts_total']);

                            if (processingPercent == 100) {
                                window.clearInterval(interval);
                                youtubeIFrame.show();
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
                        requesting = !requesting;
                    });
                }
            }, 3000);
        }
    }
});