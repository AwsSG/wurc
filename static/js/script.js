$(document).ready(function () {
    $('.sidenav').sidenav({ edge: "right" });
    $('.chips-placeholder').chips({
        placeholder: 'Enter your top skills (press enter after each skill)',
        secondaryPlaceholder: '+Tag',
    });
    $('select').formSelect();
});