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
    /* source for delete alert: https://stackoverflow.com/questions/19022176/confirm-button-before-running-deleting-routine-from-website/19022323 */
    $("a.delete").click(function (e) {
        if (!confirm('Are you sure you want to delete this job?')) {
            e.preventDefault();
            return false;
        }
        return true;
    });
    /* copyright year */
    $("#copyright").text(new Date().getFullYear());
    $('.slider').slider({interval: 6000});
});