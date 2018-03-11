$("input").keydown(function (e) {
    if (e.which === 9) {
        e.preventDefault();
        $("form").submit();
    }
});