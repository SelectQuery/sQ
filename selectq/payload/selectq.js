(function (ctx) {
    'use strict';
    function toggle_highlight(elems) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.toggle('sQ-highlight');
        }
    }

    function highlight(elems) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.add('sQ-highlight');
        }

        // must be an even number of rounds
        for (var i = 0; i < 8; i++) {
            setTimeout(function () { toggle_highlight(elems); }, 150*(i+1));
        }
    }

    function unhighlight(elems) {
        for (var i = 0; i < elems.length; i++) {
            elems[i].classList.remove('sQ-highlight');
        }
    }

    function pluck(elem, properties_names) {
        var res = [];
        for (var i = 0; i < properties_names.length; i++) {
            res.push(elem[properties_names[i]]);
        }
        return res;
    }


    if (typeof ctx.selectq === 'undefined')
        ctx.selectq = {};

    ctx.selectq.highlight = highlight;
    ctx.selectq.unhighlight = unhighlight;
    ctx.selectq.pluck = pluck;
}(window));

