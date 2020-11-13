(function (ctx) {
    'use strict';
    function toggle_highlight(elems) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.toggle('sQ-highlight');
        }
    }

    // Add the 'sQ-highlight' class to each element to highlight them
    // Remove the class from the previous selection if any.
    function highlight(elems) {
        var prev_elems = document.getElementsByClassName('sQ-highlight');

        for (var i = 0; i < prev_elems.length; i++) {
            elems[i].classList.remove('sQ-highlight');
        }

        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.add('sQ-highlight');
        }

        // must be an even number of rounds
        for (var i = 0; i < 8; i++) {
            setTimeout(function () { toggle_highlight(elems); }, 150*(i+1));
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
    ctx.selectq.pluck = pluck;
    ctx.selectq.click = click;
    ctx.selectq.add_class = add_class;
    ctx.selectq.remove_class = remove_class;
}(window));

