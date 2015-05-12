function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
/* AJAX SETUP IMPLEMENTATION */
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        // Finds if is POST method
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
        // Shows ajax loader
        $(this).addClass('loading');
    },
    complete: function(xhr, status) {
        // Hides ajax loader
        $(this).removeClass('loading');
    }
});

$(function() {
    // Saves the default jQuery load function implementation
    var oldJQLoadFn = jQuery.fn.load;

    // Overriding jQuery load function implementation to add another param to set
    // the context of the ajax request method, in order to show the ajax loader
    jQuery.fn.extend({
        load: function(e, n, r, c) {
            // Uses the default jQuery implementation if e is not an string
            if ("string" != typeof e) return oldJQLoadFn.apply(this, arguments);

            /* The rest of the jQuery load function implementation with some modifications */
            var i, o, a, s = this, l = e.indexOf(" "), context;
            return l >= 0 && (i = e.slice(l, e.length), e = e.slice(0, l)),
                (c) ? (c instanceof Element) ? (context = c) : (context = this) : (n instanceof Element) ? (context = n, n = null) : (r instanceof Element) ? (context = r) : (context = this),
                $.isFunction(n) ? (r = n, n = null) : n && "object" == typeof n && !(n instanceof Element) && (a = "POST"),
                s.length > 0 && $.ajax({url: e, type: a, dataType: "html", data: n, context: context}).done(function (e) {
                o = arguments, s.html(i ? $("<div>").append($.parseHTML(e)).find(i) : e)
            }).complete(r && function (e, t) {
                s.each(r, o || [e.responseText, t, e])
            }), this
        }
    });

    // Overriding jQuery $.get and $.post function implementations to add another param to set
    // the context of the ajax request method, in order to show the ajax loader
    jQuery.extend ({
        get: function (e, r, i, o, c) {
            var context;
            (c) ? (c instanceof Element) ? (context = c) : (context = null)
                : (r instanceof Element) ? (context = r, r = null)
                : (i instanceof Element) ? (context = i, i = null)
                : (o instanceof Element) ? (context = o, o = null)
                : (context = null);
            return $.isFunction(r) && (o = o || i, i = r, r = null), $.ajax({url: e, type: "GET", dataType: o, data: r, success: i, context: context})
        },
        post: function (e, r, i, o, c) {
            var context;
            (c) ? (c instanceof Element) ? (context = c) : (context = null)
                : (r instanceof Element) ? (context = r, r = null)
                : (i instanceof Element) ? (context = i, i = null)
                : (o instanceof Element) ? (context = o, o = null)
                : (context = null);
            return $.isFunction(r) && (o = o || i, i = r, r = null), $.ajax({url: e, type: "POST", dataType: o, data: r, success: i, context: context})
        }
    });
});