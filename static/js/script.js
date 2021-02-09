$(document).ready(function () {
    $('.sidenav').sidenav({ edge: "right" });
    $('.chips-placeholder').chips({
        placeholder: 'Enter your top skills (press enter after each skill)',
        secondaryPlaceholder: '+Tag',
    });
    $('select').formSelect();
    $('.tabs').tabs();
    $("#addExpInput").click(function () {
        $("#cloneInputs").clone(true).appendTo(".copieble_input");
    });
    $('.collapsible').collapsible();
    var elem = document.querySelector('.collapsible.expandable');
    var instance = M.Collapsible.init(elem, {
    accordion: false
    });
});