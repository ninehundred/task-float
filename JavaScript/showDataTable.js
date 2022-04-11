function showDataTable() {
  // TODO: split the Javascript up into smaller files.
  // Whenever an item within task table is clicked, do the following (as in make the input!)
  $( "#tasktable" ).on( "click", 'td:not(:first-child)', function updateData(e))
  // load up the tasktable
  $('#tasktable').DataTable( {
    // Turn off paging
    paging: false,
    // lock the header
    fixedHeader: true,
    // With dom set up the layout
    dom:'<"search"f>B<"top"l>rt<"clear">',
    // Create the following buttons (each with their own function)
    // TODO: need to add tooltips to buttons
    // TODO: need to add a couple of shortcuts to add and substract rows (this will be noted in the button tooltip)

    // Hide the first column
    'columns' : [
        { "width": "2%" }, // cant quite figure out how to hide this...
        { "width": "8%" },
        { "width": "8%" },
        { "width": "12%" },
        null,
        { "width": "6%" },
        { "width": "6%" },
        { "width": "6%" },
    ],
    buttons: [ {
        // Add row button and subsequent function
        text: 'add',
        action: function ( e, dt, node, config ) {
          //alert( 'adding a new row' );
          $.ajax({
            type: 'POST',
            url: "http://127.0.0.1:5000/tasks",
            data: JSON.stringify({
              "task_post_type" : "add_new_row",
            }),
            error: function(e) {
              console.log(e);
            },
            dataType: "json",
            contentType: "application/json"
          });
          // After we've added the new row we need to refresh the page
          window.location.reload(false);
        }
      },
      // Remove row button and subsequent function
      { text: 'remove',
        action: function ( e, dt, node, config) {
          alert( 'delete row button here' ); //maybe need extra check box to select row to delete first...?
        }
      },
      // Button to update task list (send post request)
      { text: 'complete',
        action: function ( e, dt, node, config) {
          alert( 'this will update task list' );
          }
        },
        // Remove row button and subsequent function
        { text: 'export',
          action: function ( e, dt, node, config) {
            alert( 'delete row button here' ); //maybe need extra check box to select row to delete first...?
          }
        },
      ],
    });
  });
