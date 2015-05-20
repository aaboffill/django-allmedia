$(function () {
    var ATTRIBUTE = 'attr',
        HIDE_IFRAME = 'hide',
        valueFromData = function(expression, value, progressContainer) {
            if (typeof expression == 'undefined') return;

            var elements = expression.split(':', 2);
            if (elements.length != 2) throw new Error('Expected two elements separated by ":" in the param "expression" with value "' + expression + '".');

            var selector = elements[0], methodExpression = elements[1];

            var methodParts = methodExpression.split('->', 2);
            if (methodParts.length != 2) throw new Error('Expected two elements separated by "->" in "methodExpression" with value "' + methodExpression + '".');

            var methodType = methodParts[0], methodName = methodParts[1];

            var htmlElement = (progressContainer != null) ? progressContainer.find(selector) : $(selector);
            if (value == null) {
                return (methodType == ATTRIBUTE) ? htmlElement.attr(methodName) : eval('htmlElement.' + methodName + '()');
            } else {
                return (methodType == ATTRIBUTE) ? htmlElement.attr(methodName, value) : eval('htmlElement.' + methodName + '(\'' + value +'\')');
            }
        },
        youtubeIFrames = $('.embed-youtube-video'),
        intervalList = [],
        requestingList = [];

    youtubeIFrames.each(function () {
        var $this = $(this),
            progressContainerSelector = $this.data('progressContainer'),
            progressContainer = (typeof progressContainerSelector != 'undefined') ? $(progressContainerSelector) : null,
            processingPercent = valueFromData($this.data('processingPercent'), null, progressContainer);

        if ($.isNumeric(processingPercent) && parseInt(processingPercent) != 100) {
            var url = $this.data('url'),
                hideIFrame = $this.data('whileProcessing') == HIDE_IFRAME;

            if (typeof url != 'undefined') {
                if (hideIFrame) $this.hide();

                requestingList[url] = false;
                intervalList[url] = window.setInterval(function() {
                    if (!requestingList[url]) {
                        requestingList[url] = true;
                        $.get(url, function (response) {
                            if (response['result']) {
                                processingPercent = response['processing_progress']['percent'];

                                valueFromData($this.data('processingPercent'), processingPercent, progressContainer);
                                valueFromData($this.data('processingTimeLeft'), response['processing_progress']['time_left_ms'], progressContainer);
                                valueFromData($this.data('processingProcessed'), response['processing_progress']['parts_processed'], progressContainer);
                                valueFromData($this.data('processingTotal'), response['processing_progress']['parts_total'], progressContainer);
                                valueFromData($this.data('videoStatus'), response['processing_progress']['status'], progressContainer);

                                if (processingPercent == 100) {
                                    window.clearInterval(intervalList[url]);
                                    $this.show();
                                    if (progressContainer) progressContainer.hide();
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
                }, 3000);
            }
        }
    });
});