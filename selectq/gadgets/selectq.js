(function (ctx) {
    'use strict';
    function toggle_highlight(elems) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.toggle('sQ-highlight');
        }
    }

    var toggle_highlight_callbacks = [];

    // Add the 'sQ-highlight' class to each element to highlight them
    // Remove the class from the previous selection if any.
    function highlight(elems) {
        highlight_off();

        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.add('sQ-highlight');
        }

        // must be an even number of rounds
        for (var i = 0; i < 8; i++) {
            var id = setTimeout(function () { toggle_highlight(elems); }, 150*(i+1));
            toggle_highlight_callbacks.push(id);
        }
    }

    function highlight_off() {
        // disable any toggle_highlight future call.
        for (var i = 0; i < toggle_highlight_callbacks.length; i++) {
            clearTimeout(toggle_highlight_callbacks[i]);
        }
        toggle_highlight_callbacks.length = 0;

        var prev_elems = document.getElementsByClassName('sQ-highlight');

        // The array returned by getElementsByClassName() is alive: if
        // we remove the class from the element, the array is modified
        // automatically. It is like if we were removing the elements
        // from the array itself so we cannot iterate it with a "for loop"
        while (prev_elems.length > 0) {
            prev_elems[0].classList.remove('sQ-highlight');
        }
    }

    function add_class(elems, css_class) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.add(css_class);
        }
    }

    function remove_class(elems, css_class) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.remove(css_class);
        }
    }

    // Retrieve the properties asked from the single element.
    // Dotted properties are not supported.
    function pluck(elem, properties_names) {
        var res = [];
        for (var i = 0; i < properties_names.length; i++) {
            res.push(elem[properties_names[i]]);
        }
        return res;
    }

    // Click in the element selected.
    // If single is true, do not click anything if the are
    // more than one element selected (or zero).
    function click(elems, single) {
        if (single && elems.length != 1)
            return false;

        for (var i = 0; i < elems.length; i++) {
            elems[i].click();
        }

        return true;
    }


    if (typeof ctx.selectq === 'undefined')
        ctx.selectq = {};

    ctx.selectq.highlight = highlight;
    ctx.selectq.highlight_off = highlight_off;
    ctx.selectq.pluck = pluck;
    ctx.selectq.click = click;
    ctx.selectq.add_class = add_class;
    ctx.selectq.remove_class = remove_class;
}(window));

