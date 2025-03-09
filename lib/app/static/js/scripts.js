$(document).ready(function () {

    console.log("DOM is fully loaded!");
    var table = new DataTable('#deviceTable', {
        info: false,
        searching: true,
        ordering: true,
        paging: false,
        responsive: true
    });

//    table.dataTables_filter {
//        display: none;
//    }

//    var table = $("deviceTable").DataTable({
//        paging: true,
//        searching: true,
//        ordering: true,
//        info: true,
//        lengthMenu: [5, 10, 25, 50],
//    });

    // Custom search input functionality
//    $("#customSearch").on("keyup", function () {
//        var value = $(this).val();
//        console.log("Search input:", value);
//        table.search(this.value).draw();
//    });
});

